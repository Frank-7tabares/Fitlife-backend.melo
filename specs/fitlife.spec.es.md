# Especificación de Funcionalidad: Aplicación Backend FitLife

**Creado**: 2026-01-21

## Escenarios de Usuario y Pruebas *(obligatorio)*

<!--
  Las historias de usuario están PRIORIZADAS como viajes de usuario ordenados por importancia.
  Cada historia de usuario/viaje es PROBABLE INDEPENDIENTEMENTE - lo que significa que si implementas solo UNA de ellas,
  aún deberías tener un MVP viable que entregue valor.
-->

### Historia de Usuario 1 - Registro y Autenticación de Usuario (Prioridad: P1)

Un nuevo usuario necesita registrarse en la aplicación FitLife para acceder a servicios de fitness personalizados. Proporciona su correo electrónico, contraseña e información básica de perfil. El sistema crea su cuenta y le permite iniciar sesión de forma segura usando tokens JWT.

**Por qué esta prioridad**: Esta es la base de toda la aplicación. Sin autenticación, ninguna otra funcionalidad puede operar. Es el punto de entrada para todos los usuarios.

**Prueba Independiente**: Puede probarse completamente registrando un nuevo usuario vía POST /auth/register, iniciando sesión vía POST /auth/login, y verificando que se devuelva un token JWT válido. Entrega valor inmediato al permitir a los usuarios crear cuentas y acceder al sistema.

**Escenarios de Aceptación**:

1. **Escenario**: Registro exitoso de usuario
   - **Dado** un nuevo usuario con correo electrónico y contraseña válidos
   - **Cuando** envía el registro vía POST /auth/register
   - **Entonces** el sistema crea su cuenta, devuelve un estado 201, y proporciona tokens de acceso y actualización

2. **Escenario**: Inicio de sesión de usuario con credenciales válidas
   - **Dado** un usuario registrado existente
   - **Cuando** envía credenciales de inicio de sesión vía POST /auth/login
   - **Entonces** el sistema valida las credenciales y devuelve token JWT de acceso y token de actualización

3. **Escenario**: Actualización de token
   - **Dado** un usuario con un token de acceso expirado pero token de actualización válido
   - **Cuando** solicita un nuevo token de acceso vía POST /auth/refresh
   - **Entonces** el sistema emite un nuevo token de acceso sin requerir volver a iniciar sesión

4. **Escenario**: Intento de registro inválido
   - **Dado** un usuario intentando registrarse con un correo electrónico ya utilizado
   - **Cuando** envía el registro
   - **Entonces** el sistema devuelve un error 409 Conflict con mensaje apropiado

---

### Historia de Usuario 2 - Evaluación Física Inicial (Prioridad: P1)

Un usuario recién registrado completa su evaluación física inicial respondiendo preguntas progresivas sobre su condición física, capacidad funcional, hábitos y alertas de salud. El sistema calcula su puntuación de fitness (0-100) y edad corporal estimada.

**Por qué esta prioridad**: Este es el diferenciador central de FitLife - el "diagnóstico desafiante" que motiva a los usuarios. Debe funcionar inmediatamente después del registro para involucrar a los usuarios y proporcionar recomendaciones personalizadas.

**Prueba Independiente**: Puede probarse completamente enviando una evaluación vía POST /assessments con varias combinaciones de respuestas y verificando que el sistema devuelva una puntuación calculada, estimación de edad corporal y categorización. Entrega valor inmediato al proporcionar a los usuarios su línea base de fitness.

**Escenarios de Aceptación**:

1. **Escenario**: Completar evaluación inicial
   - **Dado** un usuario registrado que no ha completado una evaluación
   - **Cuando** envía respuestas a todas las preguntas de evaluación vía POST /assessments
   - **Entonces** el sistema calcula y devuelve su puntuación de fitness (0-100), estimación de edad corporal, y categoría de fitness (Excelente/Bueno/Regular/Deficiente)

2. **Escenario**: El cálculo de edad corporal muestra que el usuario es mayor que su edad real
   - **Dado** un usuario de 30 años con indicadores de fitness pobres (IMC alto, baja capacidad funcional)
   - **Cuando** se procesa la evaluación
   - **Entonces** el sistema devuelve edadCorporal > edadReal con estado "BODY_OLDER" y un valor de diferencia positivo

3. **Escenario**: El cálculo de edad corporal muestra que el usuario es más joven que su edad real
   - **Dado** un usuario de 40 años con excelentes indicadores de fitness
   - **Cuando** se procesa la evaluación
   - **Entonces** el sistema devuelve edadCorporal < edadReal con estado "BODY_YOUNGER" y un valor de diferencia negativo

4. **Escenario**: Ver historial de evaluaciones
   - **Dado** un usuario que ha completado múltiples evaluaciones a lo largo del tiempo
   - **Cuando** solicita su historial de evaluaciones vía GET /users/{id}/assessments
   - **Entonces** el sistema devuelve todas las evaluaciones ordenadas por fecha, mostrando progreso a lo largo del tiempo

---

### Historia de Usuario 3 - Selección y Asignación de Instructor (Prioridad: P1)

Un usuario navega por los instructores disponibles, ve sus perfiles incluyendo certificaciones y calificaciones, y selecciona uno para guiar su viaje de fitness. El sistema asigna el instructor y mantiene la relación.

**Por qué esta prioridad**: La relación instructor-usuario es central al modelo de negocio. Los usuarios necesitan orientación, y los instructores necesitan clientes. Esto habilita el intercambio de valor central.

**Prueba Independiente**: Puede probarse completamente listando instructores vía GET /instructors, viendo detalles individuales de instructor vía GET /instructors/{id}, y asignando un instructor vía POST /users/{id}/assign-instructor. Entrega valor al conectar usuarios con orientación profesional.

**Escenarios de Aceptación**:

1. **Escenario**: Navegar instructores disponibles
   - **Dado** múltiples instructores registrados en el sistema
   - **Cuando** un usuario solicita la lista de instructores vía GET /instructors
   - **Entonces** el sistema devuelve todos los instructores con su nombre, certificaciones, calificación y conteo de usuarios activos

2. **Escenario**: Ver detalles de instructor
   - **Dado** un ID de instructor específico
   - **Cuando** un usuario solicita detalles del instructor vía GET /instructors/{id}
   - **Entonces** el sistema devuelve el perfil completo del instructor incluyendo certificaciones, especializaciones, calificación y número de usuarios activos

3. **Escenario**: Asignar instructor a usuario
   - **Dado** un usuario sin un instructor activo
   - **Cuando** selecciona y asigna un instructor vía POST /users/{id}/assign-instructor
   - **Entonces** el sistema crea la relación instructor-usuario y la marca como activa

4. **Escenario**: Cambiar instructor
   - **Dado** un usuario con un instructor activo
   - **Cuando** asigna un instructor diferente
   - **Entonces** el sistema desactiva la relación anterior (preservando historial) y activa la nueva

5. **Escenario**: Calificar instructor
   - **Dado** un usuario con una relación de instructor activa
   - **Cuando** envía una calificación vía POST /instructors/{id}/rate
   - **Entonces** el sistema actualiza la calificación promedio del instructor

---

### Historia de Usuario 4 - Seguimiento de Progreso Físico (Prioridad: P2)

Un usuario registra regularmente sus mediciones físicas (peso, porcentaje de grasa corporal, cintura, cadera) para rastrear su progreso a lo largo del tiempo. El sistema calcula el IMC automáticamente y almacena los datos históricos.

**Por qué esta prioridad**: El seguimiento de progreso es esencial para la motivación y para que los instructores ajusten los planes de entrenamiento. Sin embargo, los usuarios pueden comenzar a entrenar sin seguimiento extensivo, haciendo esto P2.

**Prueba Independiente**: Puede probarse completamente enviando registros físicos vía POST /users/{id}/physical-records y recuperando historial vía GET /users/{id}/physical-records. Entrega valor al mostrar a los usuarios su trayectoria de progreso.

**Escenarios de Aceptación**:

1. **Escenario**: Registrar nuevas mediciones físicas
   - **Dado** un usuario quiere registrar su estado físico actual
   - **Cuando** envía mediciones de peso, altura, % de grasa corporal, cintura y cadera vía POST /users/{id}/physical-records
   - **Entonces** el sistema almacena el registro con marca de tiempo, calcula IMC, y devuelve el registro completo

2. **Escenario**: Ver historial de progreso físico
   - **Dado** un usuario con múltiples registros físicos a lo largo del tiempo
   - **Cuando** solicita su historial vía GET /users/{id}/physical-records
   - **Entonces** el sistema devuelve todos los registros ordenados por fecha, con IMC calculado para cada uno

3. **Escenario**: Cálculo de IMC
   - **Dado** un usuario envía peso 73.5kg y altura 163cm
   - **Cuando** se procesa el registro
   - **Entonces** el sistema calcula IMC = 27.7 (peso / (altura/100)²) pero NO persiste el valor de IMC

---

### Historia de Usuario 5 - Asignación y Seguimiento de Rutina de Entrenamiento (Prioridad: P2)

Un instructor crea una rutina de entrenamiento personalizada para su usuario basada en sus objetivos y nivel de fitness. El usuario recibe la rutina, la sigue, y registra sus completaciones de entrenamiento con esfuerzo percibido y notas.

**Por qué esta prioridad**: Esta es funcionalidad central pero depende de tener un instructor asignado (P1). Los usuarios necesitan rutinas para entrenar efectivamente, pero el sistema puede funcionar con solo evaluación y asignación de instructor inicialmente.

**Prueba Independiente**: Puede probarse completamente creando una rutina vía POST /training/routines, asignándola vía POST /users/{id}/routines/assign, viendo rutina activa vía GET /users/{id}/routines/active, y completando entrenamientos vía POST /workouts/{id}/complete. Entrega valor al proporcionar orientación de entrenamiento estructurada.

**Escenarios de Aceptación**:

1. **Escenario**: Instructor crea rutina de entrenamiento
   - **Dado** un instructor quiere crear una rutina para un objetivo específico
   - **Cuando** envía detalles de rutina vía POST /training/routines con objetivo, nivel, días por semana y ejercicios
   - **Entonces** el sistema crea y almacena la rutina con todas las especificaciones de ejercicios

2. **Escenario**: Asignar rutina a usuario
   - **Dado** un instructor ha creado una rutina
   - **Cuando** la asigna a su usuario vía POST /users/{id}/routines/assign
   - **Entonces** el sistema vincula la rutina al usuario y la marca como activa

3. **Escenario**: Usuario ve rutina activa
   - **Dado** un usuario con una rutina asignada
   - **Cuando** solicita su rutina activa vía GET /users/{id}/routines/active
   - **Entonces** el sistema devuelve la rutina completa con todos los ejercicios, series, repeticiones y períodos de descanso

4. **Escenario**: Completar sesión de entrenamiento
   - **Dado** un usuario ha terminado un entrenamiento de su rutina
   - **Cuando** lo marca como completo vía POST /workouts/{id}/complete con esfuerzo percibido y notas
   - **Entonces** el sistema registra la completación con marca de tiempo, nivel de esfuerzo y notas

5. **Escenario**: Ver demostración de ejercicio
   - **Dado** un usuario viendo un ejercicio en su rutina
   - **Cuando** accede a los detalles del ejercicio
   - **Entonces** el sistema proporciona el nombre del ejercicio, grupo muscular, dificultad y URL de YouTube para demostración

---

### Historia de Usuario 6 - Gestión de Plan de Nutrición (Prioridad: P2)

Un instructor crea un plan de nutrición semanal para su usuario con sugerencias de comidas para desayuno, almuerzo y cena para cada día. El usuario puede ver su plan de nutrición activo y seguir las recomendaciones.

**Por qué esta prioridad**: La nutrición es importante para objetivos de fitness pero es secundaria al entrenamiento. Los usuarios pueden progresar con solo rutinas de entrenamiento, haciendo esto P2.

**Prueba Independiente**: Puede probarse completamente creando un plan de nutrición vía POST /nutrition/plans y viéndolo vía GET /users/{id}/nutrition/active. Entrega valor al proporcionar orientación dietética junto con el entrenamiento.

**Escenarios de Aceptación**:

1. **Escenario**: Instructor crea plan de nutrición semanal
   - **Dado** un instructor quiere proporcionar orientación nutricional
   - **Cuando** crea un plan vía POST /nutrition/plans con comidas para cada día de la semana
   - **Entonces** el sistema almacena el plan con todos los detalles de comidas y notas

2. **Escenario**: Usuario ve plan de nutrición activo
   - **Dado** un usuario con un plan de nutrición asignado
   - **Cuando** solicita su plan activo vía GET /users/{id}/nutrition/active
   - **Entonces** el sistema devuelve el plan de comidas de la semana actual con desayuno, almuerzo, cena para cada día, más notas generales

3. **Escenario**: Actualizar plan de nutrición para nueva semana
   - **Dado** un instructor quiere ajustar el plan basado en el progreso del usuario
   - **Cuando** crea un nuevo plan para la siguiente semana
   - **Entonces** el sistema almacena el nuevo plan y lo marca como activo para la semana especificada

---

### Historia de Usuario 7 - Mensajería Instructor-Usuario (Prioridad: P3)

Los instructores envían mensajes a sus usuarios para comunicar ajustes de rutina, proporcionar motivación o compartir nuevos planes de nutrición. Los usuarios pueden ver su historial de mensajes con su instructor.

**Por qué esta prioridad**: Aunque la comunicación es valiosa, el MVP se enfoca en intercambio de datos estructurados (rutinas, planes) en lugar de chat en tiempo real. Los mensajes son para mantenimiento de registros y notificaciones, no comunicación primaria.

**Prueba Independiente**: Puede probarse completamente enviando mensajes vía POST /messages y recuperándolos vía GET /messages/user/{id}. Entrega valor al habilitar comunicación asíncrona.

**Escenarios de Aceptación**:

1. **Escenario**: Instructor envía mensaje a usuario
   - **Dado** un instructor quiere notificar a su usuario sobre un ajuste de rutina
   - **Cuando** envía un mensaje vía POST /messages
   - **Entonces** el sistema almacena el mensaje con remitente, destinatario, contenido y marca de tiempo

2. **Escenario**: Usuario ve historial de mensajes
   - **Dado** un usuario ha recibido múltiples mensajes de su instructor
   - **Cuando** solicita mensajes vía GET /messages/user/{id}
   - **Entonces** el sistema devuelve todos los mensajes ordenados por marca de tiempo

3. **Escenario**: Mensajes generados por el sistema
   - **Dado** un instructor asigna una nueva rutina o plan de nutrición
   - **Cuando** se completa la asignación
   - **Entonces** el sistema automáticamente crea un mensaje notificando al usuario de la nueva asignación

---

### Historia de Usuario 8 - Recordatorios de Entrenamiento (Prioridad: P3)

Los usuarios configuran recordatorios para sus sesiones de entrenamiento, actualizaciones de registros físicos y seguimientos con instructor. El sistema envía notificaciones push vía Firebase Cloud Messaging en los tiempos programados.

**Por qué esta prioridad**: Los recordatorios mejoran la adherencia pero no son esenciales para la funcionalidad central. Los usuarios pueden entrenar sin recordatorios automatizados, haciendo esto una característica deseable para el MVP.

**Prueba Independiente**: Puede probarse completamente creando recordatorios vía POST /reminders, viéndolos vía GET /reminders, y verificando que las notificaciones se disparen en el tiempo programado. Entrega valor al mejorar el compromiso y consistencia del usuario.

**Escenarios de Aceptación**:

1. **Escenario**: Crear recordatorio de entrenamiento
   - **Dado** un usuario quiere ser recordado de entrenar
   - **Cuando** crea un recordatorio vía POST /reminders con tipo "TRAINING" y horario
   - **Entonces** el sistema almacena el recordatorio y programa una notificación

2. **Escenario**: Crear recordatorio de registro físico
   - **Dado** un usuario quiere recordar registrar sus mediciones semanalmente
   - **Cuando** crea un recordatorio con tipo "PHYSICAL_RECORD"
   - **Entonces** el sistema programa notificaciones semanales

3. **Escenario**: Ver todos los recordatorios
   - **Dado** un usuario tiene múltiples recordatorios activos
   - **Cuando** solicita sus recordatorios vía GET /reminders
   - **Entonces** el sistema devuelve todos los recordatorios activos con tipo, horario y estado

4. **Escenario**: Recibir notificación push
   - **Dado** llega el tiempo programado de un recordatorio
   - **Cuando** el sistema procesa el recordatorio
   - **Entonces** se envía una notificación push vía Firebase Cloud Messaging al dispositivo del usuario

---

### Historia de Usuario 9 - Restablecimiento y Cambio de Contraseña (Prioridad: P1)

Un usuario que olvidó su contraseña puede solicitar un restablecimiento mediante su correo electrónico. El sistema envía un token de restablecimiento con tiempo de expiración limitado. El usuario autenticado también puede cambiar su contraseña actual proporcionando la contraseña antigua y la nueva.

**Por qué esta prioridad**: La recuperación de contraseña es una funcionalidad crítica de seguridad y usabilidad. Los usuarios que olvidan sus contraseñas necesitan poder recuperar el acceso a su cuenta de forma segura. Es parte fundamental del sistema de autenticación.

**Prueba Independiente**: Puede probarse completamente solicitando restablecimiento vía POST /auth/password/reset-request, validando el token y estableciendo nueva contraseña vía POST /auth/password/reset, y cambiando contraseña para usuario autenticado vía POST /auth/password/change. Entrega valor al permitir recuperación de cuenta segura y gestión de credenciales.

**Escenarios de Aceptación**:

1. **Escenario**: Solicitar restablecimiento de contraseña
   - **Dado** un usuario registrado que olvidó su contraseña
   - **Cuando** solicita restablecimiento vía POST /auth/password/reset-request con su correo electrónico
   - **Entonces** el sistema genera un token único de restablecimiento con expiración de 1 hora, lo almacena y envía un correo electrónico con enlace de restablecimiento

2. **Escenario**: Restablecer contraseña con token válido
   - **Dado** un usuario con un token de restablecimiento válido no expirado
   - **Cuando** envía nueva contraseña vía POST /auth/password/reset con el token
   - **Entonces** el sistema valida el token, verifica requisitos de complejidad de contraseña, hashea la nueva contraseña, actualiza la cuenta, invalida el token de restablecimiento y todos los tokens de actualización existentes

3. **Escenario**: Intento de restablecimiento con token expirado
   - **Dado** un usuario con un token de restablecimiento que excedió el tiempo de expiración de 1 hora
   - **Cuando** intenta restablecer contraseña
   - **Entonces** el sistema rechaza la solicitud con error 400 indicando que el token ha expirado y debe solicitar un nuevo restablecimiento

4. **Escenario**: Intento de restablecimiento con token inválido o ya usado
   - **Dado** un usuario con un token que no existe o ya fue usado
   - **Cuando** intenta restablecer contraseña
   - **Entonces** el sistema rechaza la solicitud con error 400 indicando token inválido

5. **Escenario**: Cambiar contraseña para usuario autenticado
   - **Dado** un usuario autenticado que desea cambiar su contraseña
   - **Cuando** envía contraseña actual y nueva contraseña vía POST /auth/password/change
   - **Entonces** el sistema verifica la contraseña actual, valida requisitos de complejidad de nueva contraseña, actualiza la contraseña hasheada e invalida todos los tokens de actualización existentes excepto el actual

6. **Escenario**: Intento de cambio con contraseña actual incorrecta
   - **Dado** un usuario autenticado
   - **Cuando** intenta cambiar contraseña proporcionando contraseña actual incorrecta
   - **Entonces** el sistema rechaza la solicitud con error 401 indicando credenciales inválidas

7. **Escenario**: Prevención de reutilización de contraseña
   - **Dado** un usuario cambiando o restableciendo su contraseña
   - **Cuando** intenta usar una de las últimas 5 contraseñas previamente utilizadas
   - **Entonces** el sistema rechaza la solicitud con error 400 indicando que la contraseña ya fue utilizada recientemente

8. **Escenario**: Validación de complejidad de contraseña
   - **Dado** un usuario estableciendo una nueva contraseña
   - **Cuando** la contraseña no cumple requisitos mínimos (8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial)
   - **Entonces** el sistema rechaza la solicitud con error 400 listando los requisitos no cumplidos

---

### Historia de Usuario 10 - Actualización de Perfil de Usuario (Prioridad: P2)

Un usuario autenticado puede actualizar su información de perfil incluyendo nombre, edad, género, objetivos de fitness y preferencias. El sistema valida los cambios, previene conflictos de datos únicos y registra todas las modificaciones para auditoría.

**Por qué esta prioridad**: La actualización de perfil permite a los usuarios mantener su información actualizada y personalizar su experiencia. Aunque importante, los usuarios pueden utilizar la aplicación con su perfil inicial, haciendo esto P2.

**Prueba Independiente**: Puede probarse completamente obteniendo perfil actual vía GET /users/{id}/profile, actualizando campos vía PUT/PATCH /users/{id}/profile, y verificando validaciones y restricciones. Entrega valor al permitir personalización continua de la cuenta.

**Escenarios de Aceptación**:

1. **Escenario**: Ver perfil actual
   - **Dado** un usuario autenticado
   - **Cuando** solicita su perfil vía GET /users/{id}/profile
   - **Entonces** el sistema devuelve toda su información de perfil incluyendo nombre, correo electrónico, edad, género, altura, peso actual, objetivos de fitness, nivel de actividad y fecha de registro

2. **Escenario**: Actualizar información básica de perfil
   - **Dado** un usuario autenticado
   - **Cuando** actualiza campos editables (nombre, edad, género, altura) vía PATCH /users/{id}/profile
   - **Entonces** el sistema valida los datos, actualiza los campos especificados, registra la modificación con timestamp y devuelve el perfil actualizado

3. **Escenario**: Actualizar objetivos de fitness y preferencias
   - **Dado** un usuario autenticado
   - **Cuando** actualiza objetivos (WEIGHT_LOSS/MUSCLE_GAIN/GENERAL_FITNESS/ATHLETIC_PERFORMANCE) y nivel de actividad
   - **Entonces** el sistema actualiza las preferencias y registra el cambio para que los instructores puedan ajustar planes

4. **Escenario**: Intento de cambio de correo electrónico a uno ya registrado
   - **Dado** un usuario intenta cambiar su correo electrónico
   - **Cuando** el nuevo correo ya está registrado por otro usuario
   - **Entonces** el sistema rechaza la solicitud con error 409 Conflict indicando que el correo ya está en uso

5. **Escenario**: Cambio exitoso de correo electrónico
   - **Dado** un usuario autenticado cambiando su correo electrónico a uno disponible
   - **Cuando** envía nuevo correo vía PATCH /users/{id}/profile
   - **Entonces** el sistema valida formato del correo, verifica unicidad, envía correo de verificación a la nueva dirección, marca el correo como "pendiente de verificación" y requiere confirmación antes de que el cambio sea efectivo

6. **Escenario**: Restricción de campos no editables
   - **Dado** un usuario autenticado
   - **Cuando** intenta modificar campos no editables (ID de usuario, rol, fecha de registro, fecha de última evaluación)
   - **Entonces** el sistema ignora estos campos en la actualización o devuelve error 400 indicando campos no modificables

7. **Escenario**: Validación de rangos de datos
   - **Dado** un usuario actualizando su perfil
   - **Cuando** proporciona valores fuera de rangos válidos (edad < 13 o > 120, altura < 100cm o > 250cm)
   - **Entonces** el sistema rechaza la solicitud con error 400 indicando los rangos permitidos

8. **Escenario**: Autorización de actualización de perfil
   - **Dado** un usuario autenticado intentando actualizar un perfil
   - **Cuando** el ID del perfil no coincide con el ID del usuario autenticado (excepto ADMIN)
   - **Entonces** el sistema rechaza la solicitud con error 403 Forbidden

9. **Escenario**: Auditoría de cambios de perfil
   - **Dado** un usuario ha realizado múltiples actualizaciones de perfil
   - **Cuando** un administrador consulta el historial de auditoría del usuario
   - **Entonces** el sistema devuelve registro completo de cambios con timestamps, campos modificados, valores anteriores y nuevos valores

10. **Escenario**: Actualización parcial de perfil
    - **Dado** un usuario autenticado
    - **Cuando** envía actualización PATCH con solo algunos campos (ej., solo nombre y edad)
    - **Entonces** el sistema actualiza únicamente los campos especificados, mantiene los demás sin cambios y devuelve el perfil completo actualizado

---

### Casos Extremos

- ¿Qué sucede cuando un usuario intenta asignar un instructor que ya tiene el número máximo de usuarios activos?
- ¿Cómo maneja el sistema envíos de evaluación con respuestas incompletas o inválidas?
- ¿Qué sucede cuando un usuario intenta completar un entrenamiento que no pertenece a su rutina activa?
- ¿Cómo maneja el sistema asignaciones concurrentes de instructor (condición de carrera)?
- ¿Qué sucede cuando el token de actualización de un usuario expira?
- ¿Cómo maneja el sistema registros físicos con valores biológicamente imposibles (ej., peso negativo, 300% de grasa corporal)?
- ¿Qué sucede cuando un instructor es desactivado pero aún tiene usuarios activos asignados?
- ¿Cómo maneja el sistema diferencias de zona horaria para recordatorios de entrenamiento?
- ¿Qué sucede cuando un usuario intenta calificar un instructor al que nunca ha sido asignado?
- ¿Cómo maneja el sistema URLs de YouTube que se vuelven inválidas o son eliminadas?
- ¿Qué sucede cuando múltiples solicitudes de restablecimiento de contraseña se generan para el mismo usuario antes de que expire el primer token?
- ¿Cómo maneja el sistema intentos de restablecimiento de contraseña para correos electrónicos no registrados?
- ¿Qué sucede cuando un usuario intenta cambiar su contraseña a la misma que tiene actualmente?
- ¿Cómo previene el sistema ataques de fuerza bruta en el endpoint de restablecimiento de contraseña?
- ¿Qué sucede cuando un usuario intenta actualizar su perfil mientras su token de verificación de correo electrónico está pendiente?
- ¿Cómo maneja el sistema actualizaciones concurrentes del mismo perfil de usuario (condición de carrera)?
- ¿Qué sucede cuando un usuario intenta actualizar su correo electrónico a un formato válido pero de dominio no existente?
- ¿Cómo maneja el sistema la reversión de cambios de perfil si falla el envío de correo de verificación?

## Requisitos *(obligatorio)*

### Requisitos Funcionales

#### Identidad y Acceso (Contexto Delimitado: Identidad)

- **RF-001**: El sistema DEBE permitir a los usuarios registrarse con correo electrónico y contraseña
- **RF-002**: El sistema DEBE validar formato y unicidad del correo electrónico durante el registro
- **RF-003**: El sistema DEBE hashear contraseñas usando algoritmos seguros (bcrypt o similar) antes del almacenamiento
- **RF-004**: El sistema DEBE autenticar usuarios vía correo/contraseña y emitir tokens JWT de acceso
- **RF-005**: El sistema DEBE emitir tokens de actualización con expiración más larga que los tokens de acceso
- **RF-006**: El sistema DEBE soportar actualización de token sin requerir re-autenticación
- **RF-007**: El sistema DEBE soportar funcionalidad de cierre de sesión que invalide tokens de actualización
- **RF-008**: El sistema DEBE aplicar control de acceso basado en roles con roles: USER, INSTRUCTOR, ADMIN
- **RF-009**: El sistema DEBE requerir HTTPS para todos los endpoints de autenticación
- **RF-010**: El sistema DEBE almacenar tokens de actualización en Redis para validación y revocación rápida

##### Restablecimiento y Cambio de Contraseña

- **RF-011**: El sistema DEBE permitir a usuarios solicitar restablecimiento de contraseña vía correo electrónico registrado
- **RF-012**: El sistema DEBE generar tokens de restablecimiento únicos, criptográficamente seguros con expiración de 1 hora
- **RF-013**: El sistema DEBE enviar correo electrónico con enlace de restablecimiento que contenga el token
- **RF-014**: El sistema DEBE invalidar token de restablecimiento después de uso exitoso o expiración
- **RF-015**: El sistema DEBE validar complejidad de contraseña: mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial
- **RF-016**: El sistema DEBE prevenir reutilización de las últimas 5 contraseñas del usuario
- **RF-017**: El sistema DEBE mantener historial hasheado de contraseñas previas para validación de reutilización
- **RF-018**: El sistema DEBE requerir confirmación de contraseña (doble entrada) en operaciones de restablecimiento y cambio
- **RF-019**: El sistema DEBE invalidar todos los tokens de actualización existentes al cambiar/restablecer contraseña
- **RF-020**: El sistema DEBE permitir a usuarios autenticados cambiar su contraseña proporcionando contraseña actual
- **RF-021**: El sistema DEBE verificar contraseña actual antes de permitir cambio de contraseña
- **RF-022**: El sistema DEBE registrar eventos de restablecimiento y cambio de contraseña para auditoría de seguridad
- **RF-023**: El sistema DEBE implementar límite de velocidad (rate limiting) para solicitudes de restablecimiento (máx. 3 por hora por correo)
- **RF-024**: El sistema DEBE manejar solicitudes de restablecimiento para correos no registrados sin revelar existencia de cuenta
- **RF-025**: El sistema DEBE invalidar tokens de restablecimiento anteriores al generar uno nuevo para el mismo usuario

##### Gestión de Perfil de Usuario

- **RF-026**: El sistema DEBE permitir a usuarios autenticados ver su perfil completo vía GET /users/{id}/profile
- **RF-027**: El sistema DEBE soportar actualización parcial de perfil usando método PATCH
- **RF-028**: El sistema DEBE definir campos editables: nombre, edad, género, altura, objetivos de fitness, nivel de actividad
- **RF-029**: El sistema DEBE definir campos NO editables: ID de usuario, rol, fecha de registro, correo electrónico (requiere verificación)
- **RF-030**: El sistema DEBE validar rangos de datos: edad (13-120 años), altura (100-250 cm)
- **RF-031**: El sistema DEBE validar formato de correo electrónico en cambios de correo
- **RF-032**: El sistema DEBE verificar unicidad de correo electrónico antes de permitir cambio
- **RF-033**: El sistema DEBE enviar correo de verificación al cambiar dirección de correo electrónico
- **RF-034**: El sistema DEBE marcar nuevo correo como "pendiente de verificación" hasta confirmación
- **RF-035**: El sistema DEBE permitir solo al propietario o ADMIN actualizar un perfil (autorización)
- **RF-036**: El sistema DEBE registrar todas las modificaciones de perfil para auditoría con timestamp
- **RF-037**: El sistema DEBE almacenar historial de auditoría con: usuario, timestamp, campos modificados, valor anterior, valor nuevo
- **RF-038**: El sistema DEBE soportar objetivos de fitness: WEIGHT_LOSS, MUSCLE_GAIN, GENERAL_FITNESS, ATHLETIC_PERFORMANCE, HEALTH_MAINTENANCE
- **RF-039**: El sistema DEBE devolver perfil completo actualizado después de modificaciones exitosas
- **RF-040**: El sistema DEBE aplicar bloqueo optimista para prevenir conflictos de actualización concurrente
- **RF-041**: El sistema DEBE ignorar silenciosamente campos no editables en solicitudes de actualización o devolver error 400
- **RF-042**: El sistema DEBE validar que cambios de género sean valores permitidos: MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY

#### Gestión de Instructores (Contexto Delimitado: Instructores)

- **RF-043**: El sistema DEBE permitir listar todos los instructores disponibles
- **RF-044**: El sistema DEBE mostrar perfil de instructor incluyendo nombre, certificaciones, calificación y conteo de usuarios activos
- **RF-045**: El sistema DEBE permitir a los usuarios asignarse un instructor
- **RF-046**: El sistema DEBE aplicar que un usuario puede tener solo UN instructor activo a la vez
- **RF-047**: El sistema DEBE preservar relaciones históricas instructor-usuario al cambiar instructores
- **RF-048**: El sistema DEBE permitir a los usuarios calificar a su instructor asignado (escala 1-5)
- **RF-049**: El sistema DEBE calcular y actualizar la calificación promedio del instructor basada en todas las calificaciones de usuarios
- **RF-050**: El sistema DEBE prevenir que usuarios califiquen instructores a los que no han sido asignados

#### Evaluación Física (Contexto Delimitado: Evaluación)

- **RF-051**: El sistema DEBE proporcionar preguntas de evaluación progresivas en categorías: Física, Funcional, Hábitos, Alertas
- **RF-052**: El sistema DEBE soportar tipos de pregunta: NUMERIC, SINGLE_CHOICE, MULTIPLE_CHOICE, YES_NO
- **RF-053**: El sistema DEBE calcular puntuación de fitness en escala 0-100 basada en respuestas ponderadas
- **RF-054**: El sistema DEBE categorizar puntuaciones de fitness: Excelente (90-100), Bueno (70-89), Regular (50-69), Deficiente (<50)
- **RF-055**: El sistema DEBE calcular edad corporal estimada usando fórmula: edadReal + ajuste IMC + ajuste grasa corporal + ajuste funcional + ajuste hábitos
- **RF-056**: El sistema DEBE devolver estado de comparación de edad corporal: BODY_OLDER, BODY_YOUNGER, o BODY_EQUAL
- **RF-057**: El sistema DEBE almacenar historial completo de evaluaciones para cada usuario
- **RF-058**: El sistema DEBE mostrar descargo que la edad corporal es una estimación, no diagnóstico médico
- **RF-059**: El sistema DEBE validar respuestas de evaluación contra restricciones de pregunta (valores mín/máx, opciones válidas)

#### Seguimiento de Progreso Físico (Contexto Delimitado: Progreso)

- **RF-060**: El sistema DEBE permitir a los usuarios registrar mediciones físicas: peso (kg), altura (cm), % grasa corporal, cintura (cm), cadera (cm)
- **RF-061**: El sistema DEBE registrar nivel de actividad: SEDENTARY, LIGHT, MODERATE, ACTIVE, VERY_ACTIVE
- **RF-062**: El sistema DEBE calcular IMC usando fórmula: peso / (altura/100)²
- **RF-063**: El sistema NO DEBE persistir valores de IMC calculados (calcular solo bajo demanda)
- **RF-064**: El sistema DEBE marcar temporalmente todos los registros físicos con recordedAt
- **RF-065**: El sistema DEBE permitir a los usuarios recuperar su historial completo de registros físicos
- **RF-066**: El sistema DEBE ordenar registros físicos por recordedAt descendente (más reciente primero)
- **RF-067**: El sistema DEBE validar mediciones físicas contra rangos realistas

#### Gestión de Entrenamiento (Contexto Delimitado: Entrenamiento)

- **RF-068**: El sistema DEBE permitir a instructores crear rutinas de entrenamiento con objetivo, nivel y días por semana
- **RF-069**: El sistema DEBE soportar niveles de fitness: BEGINNER, INTERMEDIATE, ADVANCED
- **RF-070**: El sistema DEBE permitir que las rutinas contengan múltiples ejercicios con series, repeticiones y períodos de descanso
- **RF-071**: El sistema DEBE almacenar biblioteca de ejercicios con nombre, grupo muscular, nivel de dificultad y URL de demostración de YouTube
- **RF-072**: El sistema DEBE soportar grupos musculares: Pecho, Espalda, Piernas, Hombros, Brazos, Core, Cuerpo Completo
- **RF-073**: El sistema DEBE soportar niveles de dificultad: LOW, MEDIUM, HIGH
- **RF-074**: El sistema DEBE permitir a instructores asignar rutinas a sus usuarios
- **RF-075**: El sistema DEBE aplicar que los usuarios pueden tener solo UNA rutina activa a la vez
- **RF-076**: El sistema DEBE permitir a los usuarios ver su rutina activa con todos los detalles de ejercicios
- **RF-077**: El sistema DEBE permitir a los usuarios marcar entrenamientos como completos con esfuerzo percibido (1-10) y notas
- **RF-078**: El sistema DEBE marcar temporalmente completaciones de entrenamiento
- **RF-079**: El sistema DEBE preservar asignaciones históricas de rutina cuando se asignan nuevas rutinas

#### Gestión de Nutrición (Contexto Delimitado: Nutrición)

- **RF-080**: El sistema DEBE permitir a instructores crear planes de nutrición semanales
- **RF-081**: El sistema DEBE soportar tipos de comida: desayuno, almuerzo, cena, snacks
- **RF-082**: El sistema DEBE organizar planes de nutrición por semana (formato ISO semana: YYYY-Www)
- **RF-083**: El sistema DEBE soportar especificaciones de comidas diarias para cada día de la semana
- **RF-084**: El sistema DEBE permitir notas/recomendaciones generales en planes de nutrición (ej., ingesta de agua)
- **RF-085**: El sistema DEBE permitir a instructores asignar planes de nutrición a sus usuarios
- **RF-086**: El sistema DEBE permitir a los usuarios ver su plan de nutrición activo
- **RF-087**: El sistema DEBE soportar actualización de planes de nutrición para nuevas semanas

#### Mensajería (Contexto Delimitado: Mensajería)

- **RF-088**: El sistema DEBE permitir a instructores enviar mensajes a sus usuarios
- **RF-089**: El sistema DEBE almacenar mensajes con remitente, destinatario, contenido y marca de tiempo
- **RF-090**: El sistema DEBE permitir a los usuarios recuperar su historial de mensajes
- **RF-091**: El sistema DEBE ordenar mensajes por marca de tiempo descendente (más reciente primero)
- **RF-092**: El sistema DEBE generar automáticamente mensajes cuando se asignan rutinas o planes de nutrición
- **RF-093**: El sistema DEBE aplicar que instructores solo pueden enviar mensajes a sus usuarios asignados
- **RF-094**: El sistema DEBE soportar tipos de mensaje: INSTRUCTOR_MESSAGE, SYSTEM_NOTIFICATION

#### Notificaciones y Recordatorios (Contexto Delimitado: Notificaciones)

- **RF-095**: El sistema DEBE permitir a los usuarios crear recordatorios con tipo y horario
- **RF-096**: El sistema DEBE soportar tipos de recordatorio: TRAINING, PHYSICAL_RECORD, INSTRUCTOR_FOLLOWUP
- **RF-097**: El sistema DEBE permitir a los usuarios ver todos sus recordatorios activos
- **RF-098**: El sistema DEBE enviar notificaciones push vía Firebase Cloud Messaging en tiempos programados
- **RF-099**: El sistema DEBE permitir a los usuarios actualizar o eliminar recordatorios
- **RF-100**: El sistema DEBE manejar conversiones de zona horaria para programación de recordatorios

#### Calidad de Datos y Validación

- **RF-101**: El sistema DEBE validar todos los payloads de solicitud API contra esquemas definidos
- **RF-102**: El sistema DEBE devolver códigos de estado HTTP apropiados (200, 201, 400, 401, 403, 404, 409, 500)
- **RF-103**: El sistema DEBE devolver respuestas de error estructuradas con código de error y mensaje
- **RF-104**: El sistema DEBE registrar todas las solicitudes API con marca de tiempo, usuario, endpoint y estado de respuesta
- **RF-105**: El sistema DEBE registrar todos los eventos de autenticación (inicio de sesión, cierre de sesión, actualización de token, fallos)
- **RF-106**: El sistema DEBE implementar versionado de API (ej., /v1/...)
- **RF-107**: El sistema DEBE persistir todos los datos en PostgreSQL con índices apropiados
- **RF-108**: El sistema DEBE usar Redis para cachear datos accedidos frecuentemente (listas de instructores, biblioteca de ejercicios)

### Entidades Clave *(incluir si la funcionalidad involucra datos)*

#### Contexto de Identidad

- **User (Usuario)**: Representa un usuario registrado con correo electrónico, contraseña hasheada, rol (USER/INSTRUCTOR/ADMIN) e información de perfil. Identificador único (UUID). Relacionado con PhysicalRecords, Assessments, InstructorAssignments, Routines, NutritionPlans, Messages, Reminders.

- **RefreshToken (Token de Actualización)**: Representa un token de actualización activo con valor de token, referencia de usuario, marca de tiempo de expiración y estado de revocación. Almacenado en Redis para búsqueda rápida.

- **PasswordResetToken (Token de Restablecimiento de Contraseña)**: Representa un token único generado para restablecimiento de contraseña con valor de token (hash criptográfico), referencia de usuario, marca de tiempo de creación, marca de tiempo de expiración (1 hora), y estado (ACTIVE, USED, EXPIRED). Identificador único (UUID). Almacenado en PostgreSQL.

- **PasswordHistory (Historial de Contraseñas)**: Representa contraseñas previas del usuario (hasheadas) para prevenir reutilización. Contiene referencia de usuario, contraseña hasheada y marca de tiempo de creación. Se mantienen las últimas 5 contraseñas por usuario.

- **UserProfile (Perfil de Usuario)**: Representa información extendida de perfil del usuario con nombre completo, fecha de nacimiento/edad, género, altura (cm), objetivos de fitness, nivel de actividad preferido, foto de perfil (URL), biografía, zona horaria y preferencias de notificación. Relacionado 1:1 con User.

- **ProfileAuditLog (Registro de Auditoría de Perfil)**: Representa cambios históricos en perfil de usuario con referencia de usuario, referencia de usuario modificador (puede ser admin), marca de tiempo, campos modificados (JSON), valores anteriores (JSON) y valores nuevos (JSON). Identificador único (UUID).

#### Contexto de Instructores

- **Instructor**: Representa un instructor de fitness con nombre, certificaciones (lista), especializaciones, calificación promedio (calculada) y conteo de usuarios activos. Identificador único (UUID). Relacionado con Users a través de InstructorAssignment.

- **InstructorAssignment (Asignación de Instructor)**: Representa la relación entre un usuario e instructor con fecha de inicio, fecha de fin (null si está activo) y estado activo. Mantiene registro histórico de todas las asignaciones.

- **InstructorRating (Calificación de Instructor)**: Representa la calificación de un usuario a su instructor con valor de calificación (1-5), marca de tiempo y comentario opcional. Usado para calcular calificación promedio del instructor.

#### Contexto de Evaluación

- **AssessmentQuestion (Pregunta de Evaluación)**: Representa una pregunta en la evaluación física con ID, tipo (NUMERIC/SINGLE_CHOICE/MULTIPLE_CHOICE/YES_NO), etiqueta, categoría (PHYSICAL/FUNCTIONAL/HABITS/ALERTS), peso para puntuación y restricciones (mín/máx, opciones).

- **Assessment (Evaluación)**: Representa una evaluación completada con referencia de usuario, marca de tiempo de envío, respuestas (mapa de questionId a valor de respuesta), puntuación de fitness calculada (0-100), categoría de fitness, edad real, edad corporal calculada, diferencia de edad y estado de edad corporal.

#### Contexto de Progreso

- **PhysicalRecord (Registro Físico)**: Representa una instantánea de mediciones físicas del usuario con peso (kg), altura (cm), porcentaje de grasa corporal, cintura (cm), cadera (cm), nivel de actividad y marca de tiempo recordedAt. El IMC se calcula bajo demanda, no se almacena.

#### Contexto de Entrenamiento

- **Exercise (Ejercicio)**: Representa un ejercicio en la biblioteca con nombre, grupo muscular, nivel de dificultad, descripción y URL de demostración de YouTube. Identificador único (UUID).

- **Routine (Rutina)**: Representa una rutina de entrenamiento con descripción de objetivo, nivel de fitness, días por semana y lista de ejercicios de rutina. Identificador único (UUID). Creada por instructores.

- **RoutineExercise (Ejercicio de Rutina)**: Representa un ejercicio dentro de una rutina con referencia de ejercicio, series, repeticiones, segundos de descanso y orden en rutina.

- **RoutineAssignment (Asignación de Rutina)**: Representa asignación de una rutina a un usuario con fecha de asignación, estado activo y fecha de fin (null si está activo).

- **WorkoutCompletion (Completación de Entrenamiento)**: Representa una sesión de entrenamiento completada con referencia de rutina, marca de tiempo de completación, esfuerzo percibido (1-10) y notas opcionales.

#### Contexto de Nutrición

- **NutritionPlan (Plan de Nutrición)**: Representa un plan de nutrición semanal con identificador de semana (formato ISO), lista de comidas diarias, notas generales y referencia de creador (instructor). Identificador único (UUID).

- **DailyMeal (Comida Diaria)**: Representa comidas para un día específico con día de la semana, desayuno, almuerzo, cena y snacks opcionales.

- **NutritionAssignment (Asignación de Nutrición)**: Representa asignación de un plan de nutrición a un usuario con fecha de asignación, estado activo y fecha de fin (null si está activo).

#### Contexto de Mensajería

- **Message (Mensaje)**: Representa un mensaje entre instructor y usuario con referencia de remitente, referencia de destinatario, contenido, tipo de mensaje (INSTRUCTOR_MESSAGE/SYSTEM_NOTIFICATION), marca de tiempo y estado de lectura.

#### Contexto de Notificaciones

- **Reminder (Recordatorio)**: Representa un recordatorio programado con referencia de usuario, tipo de recordatorio (TRAINING/PHYSICAL_RECORD/INSTRUCTOR_FOLLOWUP), horario (expresión cron o datetime específico), estado activo y marca de tiempo de creación.

- **NotificationLog (Registro de Notificación)**: Representa una notificación enviada con referencia de recordatorio, marca de tiempo de envío, estado de entrega e ID de mensaje de Firebase.

## Criterios de Éxito *(obligatorio)*

### Resultados Medibles

- **CE-001**: Los usuarios pueden completar el flujo de registro e inicio de sesión en menos de 1 minuto con 95% de tasa de éxito
- **CE-002**: Los usuarios pueden completar la evaluación física inicial en menos de 5 minutos
- **CE-003**: El cálculo de edad corporal se completa en menos de 500ms para cualquier envío de evaluación
- **CE-004**: El sistema soporta 100-500 usuarios concurrentes sin degradación de rendimiento (tiempo de respuesta < 1s para percentil 95)
- **CE-005**: Los endpoints de API devuelven respuestas dentro de 200ms para el 90% de las solicitudes (excluyendo cálculos complejos)
- **CE-006**: El cálculo de puntuación de evaluación es consistente - las mismas respuestas siempre producen la misma puntuación
- **CE-007**: El 90% de los usuarios asignan exitosamente un instructor en su primer intento
- **CE-008**: Las actualizaciones de calificación de instructor se reflejan en el perfil del instructor dentro de 1 segundo
- **CE-009**: Los usuarios pueden ver su rutina activa y plan de nutrición dentro de 2 toques/clics
- **CE-010**: El registro de completación de entrenamiento toma menos de 30 segundos
- **CE-011**: La recuperación de historial de registros físicos devuelve resultados en menos de 300ms para usuarios con hasta 100 registros
- **CE-012**: El sistema mantiene 99.9% de tiempo de actividad durante horas de negocio (6 AM - 11 PM hora local)
- **CE-013**: Cero pérdida de datos para evaluaciones completadas, registros de entrenamiento y registros físicos
- **CE-014**: Todos los endpoints de autenticación aplican HTTPS con validación de certificado apropiada
- **CE-015**: El mecanismo de token de actualización reduce fricción de inicio de sesión - los usuarios permanecen conectados por 30 días con token de actualización válido
- **CE-016**: Las notificaciones push se entregan dentro de 1 minuto del tiempo de recordatorio programado para el 95% de los recordatorios
- **CE-017**: La documentación de API (OpenAPI 3.1) cubre el 100% de los endpoints con ejemplos de solicitud/respuesta
- **CE-018**: Todos los endpoints devuelven códigos de estado HTTP apropiados y mensajes de error estructurados
- **CE-019**: Las consultas de base de datos usan índices apropiados - sin escaneos de tabla completa para operaciones comunes
- **CE-020**: Tasa de aciertos de caché de Redis > 80% para consultas de listas de instructores y biblioteca de ejercicios
- **CE-021**: El flujo de restablecimiento de contraseña se completa en menos de 3 minutos desde solicitud hasta confirmación con 90% de tasa de éxito
- **CE-022**: Los correos electrónicos de restablecimiento de contraseña se entregan dentro de 30 segundos de la solicitud para el 95% de los casos
- **CE-023**: Los tokens de restablecimiento de contraseña expiran exactamente después de 1 hora sin desviación
- **CE-024**: El sistema previene 100% de intentos de reutilización de las últimas 5 contraseñas
- **CE-025**: Las validaciones de complejidad de contraseña rechazan contraseñas débiles con 100% de precisión
- **CE-026**: El rate limiting de restablecimiento de contraseña previene más de 3 solicitudes por hora por correo electrónico
- **CE-027**: Las actualizaciones de perfil se persisten en base de datos en menos de 200ms
- **CE-028**: Los cambios de correo electrónico requieren verificación - 0% de cambios sin confirmación
- **CE-029**: El sistema registra 100% de modificaciones de perfil en auditoría con todos los campos requeridos
- **CE-030**: Las validaciones de autorización previenen 100% de intentos de modificación no autorizada de perfiles
- **CE-031**: La recuperación de historial de auditoría de perfil devuelve resultados en menos de 500ms para hasta 1000 registros
- **CE-032**: Las actualizaciones concurrentes de perfil no causan pérdida de datos ni inconsistencias (0 errores de condición de carrera)
