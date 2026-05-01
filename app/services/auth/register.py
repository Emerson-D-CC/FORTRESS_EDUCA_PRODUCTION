from datetime import timedelta, date

# FUNCIONES DE FLASK
from flask import render_template, request, redirect, url_for, flash, session, current_app, make_response

# CONFIGURACIONES LOCALES
from app.forms.auth_forms import RegisterForm
from app.repositories.auth_repository import (
    sp_obtener_barrios,
    sp_obtener_parentesco_acu,
    sp_obtener_tipos_documento,
    sp_usuario_existe,
    sp_registrar_usuario,
)

# SEGURIDAD
from app.security.recaptcha_controller import validar_recaptcha

# UTILIDADES
from app.utils.password_utils import hashear_contraseña
from app.utils.database_utils import db

# ====================================================================================================================================================
#                                           PAGINA REGISTER.HTML
# ====================================================================================================================================================

class Register_Service:
    
    def __init__(self):
        self.fecha_max = (date.today() - timedelta(days=1))
        self.fecha_min = (date.today().replace(year=date.today().year - 100))
    
    def _form_registro_acudiente(self, form):
        """Pobla las opciones de listas desplegables del formulario de registro"""
        try:
            barrio = sp_obtener_barrios()
            parentesco = sp_obtener_parentesco_acu()
            tipos_documento = sp_obtener_tipos_documento()
            
            # Poblar SelectField: Barrio
            form.barrio.choices = (
                [(0, "— Seleccione un Barrio —")] +
                [(bar["ID_Barrio"], bar["Nombre_Barrio"]) for bar in barrio]
            )   
            
            # Poblar SelectField: Parentesco
            form.parentesco.choices = (
                [(0, "— Seleccione un Parentesco —")] +
                [(par["ID_Parentesco"], par["Nombre_Parentesco"]) for par in parentesco]
            )            
                    
            # Poblar SelectField: Tipo de Documento
            form.tipo_documento.choices = (
                [(0, "— Seleccione una Identificación —")] +
                [(doc["ID_Tipo_Iden"], doc["Nombre_Tipo_Iden"]) for doc in tipos_documento]
            )            
                    
        except Exception as e:
            print(f"[ERROR] Error al cargar opciones de formulario: {e}")
            flash("Error al cargar el formulario. Intente nuevamente.", "danger")
 
 
    def Register(self):
        """Maneja las solicitudes GET y POST del formulario de registro"""
        
        form = RegisterForm()
        
        # Poblar opciones de SelectField desde la BD
        self._form_registro_acudiente(form)
        
        # =====================================================
        # SOLICITUD GET: Renderizar formulario vacío o con errores previos
        
        if request.method == "GET":
            # Verificar si hay errores y datos previos en sesión (de un POST fallido)
            if 'form_errors' in session:
                # Repoblar el formulario con datos previos
                form_data = session.pop('form_data', {})
                for field_name, value in form_data.items():
                    if hasattr(form, field_name):
                        field = getattr(form, field_name)
                        if field_name == 'terms':
                            # Checkbox: presente significa True
                            field.data = True
                        else:
                            field.data = value
                
                # Mostrar errores previos
                form_errors = session.pop('form_errors', {})
                for field_name, errors in form_errors.items():
                    if hasattr(form, field_name):
                        getattr(form, field_name).errors = errors
                
                # Flash message si hay
                if 'flash_message' in session:
                    flash(session.pop('flash_message'), session.pop('flash_category', 'danger'))
            
            response = make_response(
                render_template(
                    "auth/register.html",
                    form=form,
                    recaptcha_site_key=current_app.config.get("RECAPTCHA_SITE_KEY", ""),
                    recaptcha_error=None,
                    fecha_min=self.fecha_min,
                    fecha_max=self.fecha_max
                )
            )
            
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            return response
        
        # =====================================================
        # SOLICITUD POST: Procesar registro
        
        if request.method == "POST":
 
            # Validar reCAPTCHA            
            token_recaptcha = request.form.get("g-recaptcha-response", "")
 
            if not token_recaptcha:
                # Usuario no completó el widget de reCAPTCHA
                session['form_data'] = request.form.to_dict()
                session['form_errors'] = {}
                session['flash_message'] = "Por favor complete la verificación reCAPTCHA antes de continuar."
                session['flash_category'] = "danger"
                return redirect(url_for("auth.register"))
 
            if not validar_recaptcha(token_recaptcha):
                # Token inválido o expirado
                session['form_data'] = request.form.to_dict()
                session['form_errors'] = {}
                session['flash_message'] = "La verificación reCAPTCHA falló o expiró. Intente nuevamente."
                session['flash_category'] = "danger"
                return redirect(url_for("auth.register"))
 
            # Validar formulario (WTForms)
            
            # Ejecuta todos los validadores personalizados
            if not form.validate_on_submit():
                
                # Imprimir errores en consola para debugging
                errores = "; ".join(
                    f"{field}: {', '.join(msgs)}"
                    for field, msgs in form.errors.items()
                )
                print(f"[VALIDACIÓN] Errores en el formulario: {errores}")
                
                session['form_data'] = request.form.to_dict()
                session['form_errors'] = form.errors
                session['flash_message'] = "Error con el formulario. Por favor revise los campos."
                session['flash_category'] = "danger"
                return redirect(url_for("auth.register"))
 
            try:
                # Verificar si el documento o correo ya están registrados
                user_exists = sp_usuario_existe(form.email.data, form.documento.data)
 
                if user_exists:
                    # El usuario ya existe
                    session['form_data'] = request.form.to_dict()
                    session['form_errors'] = {}
                    session['flash_message'] = "El documento o correo electrónico ya está registrado en el sistema. Si olvidó su contraseña, use la opción 'Recuperar contraseña'."
                    session['flash_category'] = "warning"
                    return redirect(url_for("auth.register"))
 
            except Exception as e:
                print(f"[ERROR] Error al verificar usuario: {e}")
                session['form_data'] = request.form.to_dict()
                session['form_errors'] = {}
                session['flash_message'] = "Error al procesar su registro. Intente nuevamente más tarde."
                session['flash_category'] = "danger"
                return redirect(url_for("auth.register"))
 
            # Procesar datos y crear cuenta
            try:
                # Generar hash seguro de la contraseña
                hash_password = hashear_contraseña(form.password.data)
                
                # Capturar datos de auditoría
                ip = request.remote_addr
                user_agent = request.headers.get("User-Agent", "")
 
                # Llamar al stored procedure para registrar usuario     
                sp_registrar_usuario((
                    # DATOS PERSONA
                    form.documento.data,
                    form.primer_nombre.data.strip(),
                    form.segundo_nombre.data.strip() if form.segundo_nombre.data else None,
                    form.primer_apellido.data.strip(),
                    form.segundo_apellido.data.strip() if form.segundo_apellido.data else None,
                    form.fecha_nacimiento.data,
 
                    # DATOS CONTACTO
                    form.email.data.lower(),
                    form.telefono.data.strip(),
                    form.parentesco.data,
                    form.tipo_documento.data,
                    1,  # ID Genero
                    1,  # ID Grupo Preferencial (valor default)
                    1,  # ID Estrato
                    form.barrio.data,
 
                    # DATOS USUARIO
                    form.email.data.lower(),
                    hash_password,
                    2,  # ID Rol
 
                    # AUDITORÍA
                    ip,
                    user_agent
                ))
                
                # Confirmar cambios en BD
                db.commit()
                
                # Limpiar cualquier dato de sesión
                session.pop('form_data', None)
                session.pop('form_errors', None)
                session.pop('flash_message', None)
                session.pop('flash_category', None)
                
                # Mostrar mensaje de éxito
                flash("Cuenta creada correctamente. Ya puede iniciar sesión con sus credenciales.", "success")
                
                # Redirigir a login
                return redirect(url_for("auth.login_user"))
 
            except Exception as e:
                # Revertir cambios en BD en caso de error
                db.rollback()
                
                print(f"[ERROR] Registro fallido: {e}")
                
                # Mostrar mensaje de error genérico al usuario
                session['form_data'] = request.form.to_dict()
                session['form_errors'] = {}
                session['flash_message'] = "Ocurrió un error al crear la cuenta. Intente nuevamente o contacte al administrador."
                session['flash_category'] = "danger"
                return redirect(url_for("auth.register"))
 