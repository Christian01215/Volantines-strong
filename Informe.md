VOLANTINES STRONG
Informe final del proyecto
Sistema de comercio electrónico y gestión de pedidos
Taller de Sistemas de Información • UTEM

VOLANTINES STRONG | INFORME FINAL
ÍNDICE
1. Introducción.......................................................................................................................4
2. Descripción General de la Empresa.................................................................................5
2.1. Rubro y ubicación de la empresa.............................................................................5
2.2. Productos y servicios...............................................................................................5
2.3. Organigrama simplificado de la empresa.................................................................6
2.3. Problema a abordar..................................................................................................7
2.4. Organización interna................................................................................................7
3. Objetivos...........................................................................................................................8
3.1. Objetivo General del Proyecto.................................................................................8
3.2. Objetivos Específicos del Proyecto..........................................................................8
4. Descripción General del Problema...................................................................................9
4.1. Forma actual de resolución del problema................................................................9
4.2. Almacenamiento y Procesamiento de Datos Actual................................................9
4.3. Flujo de Datos Actual y Propuesto.........................................................................10
4.4. Tipos de Usuarios Existentes y Necesarios...........................................................10
4.5. Diagrama de Flujo del Proceso..............................................................................11
5. Toma de Requerimientos.................................................................................................11
5.1. Requerimientos Funcionales..................................................................................11
5.2. Requerimientos No Funcionales............................................................................12
6. Alcance y Limitaciones del Proyecto...............................................................................13
6.1. Alcance...................................................................................................................13
6.2. Limitaciones...........................................................................................................13
7. Organización del Grupo Proyecto...................................................................................14
7.1. Estructura de toma de decisiones y distribución de trabajo...................................15
7.2. Roles y responsabilidades de cada integrante.......................................................15
8. Fases del Proyecto.........................................................................................................16
8.1. Fase 0 Lanzamiento...............................................................................................16
8.2. Fase 1: Diseño e implementación..........................................................................16
8.3. Fase 2: Desarrollo y producción.............................................................................17
8.4. Fase 3: Validación..................................................................................................17
8.5. Fase Post: Evaluación e informes finales..............................................................18
9. Diseño del Sistema.........................................................................................................18
9.1. Metodología utilizada.............................................................................................18
9.2. Requerimientos del sistema...................................................................................19
9.3. Modelo Entidad-Relación.......................................................................................20
9.4. Modelo Físico-Relacional.......................................................................................21
9.5. Modelo Físico-Relacional Normalizado (1FN, 2FN y 3FN)....................................22
10. Desarrollo del Sistema..................................................................................................23
Taller de Sistemas de Información • UTEM | Página
2

VOLANTINES STRONG | INFORME FINAL
10.1. Login y autenticación............................................................................................23
10.2. Niveles de acceso y acciones de usuarios...........................................................24
10.3. Vistas del sistema................................................................................................24
10.4. Reportes del sistema............................................................................................25
11. Análisis de Riesgos.......................................................................................................26
11.1. Riesgos identificados............................................................................................26
11.2. Planes de mitigación............................................................................................28
11.3. Conclusiones sobre riesgos.................................................................................29
12. Manejo de Crisis...........................................................................................................30
12.1. Problemas que generaron crisis...........................................................................30
12.2. Tiempo y acciones de solución............................................................................30
12.3. Efectos colaterales y replanificación....................................................................31
13. Plan de Trabajo.............................................................................................................31
13.1. Cronograma de actividades.................................................................................31
13.2. Plan estimado vs real...........................................................................................32
13.3. Responsables por tareas.....................................................................................33
13.4. Costos en tiempo y dinero....................................................................................33
13.5. Estado del proyecto en la entrega final................................................................34
14. Plan de Continuidad y Riesgos Post Producción..........................................................34
14.1. Principales riesgos posteriores a la implementación...........................................34
14.2. Implicaciones en las operaciones........................................................................35
14.3. Plan de mantenimiento y mitigación.....................................................................35
15. Conclusiones.................................................................................................................37
15.1. Consecuencias de la implementación del proyecto de la empresa.....................37
15.2. Problemas enfrentados durante la ejecución del proyecto..................................38
15.3. Aprendizajes de la asignatura y su aplicabilidad futura.......................................39
15.4. Aspectos relevantes del proyecto........................................................................40
16. Anexos..........................................................................................................................41
16.1. Anexo 1 acta de reuniones...................................................................................41
16.1.1. Acta de reunión 1........................................................................................41
16.1.2. Acta de reunión 2........................................................................................43
16.1.3. Acta de reunión 3........................................................................................45
16.2. Diagramas complementarios................................................................................47
16.2.1. Diagrama de Flujo de Datos Actual.............................................................47
16.2.2. Diagrama de Flujo de Datos Propuesto......................................................47
16.2.3. Diagrama de Flujo del Proceso de Venta y Retiro......................................48
16.3. Enlaces del proyecto............................................................................................48
Taller de Sistemas de Información • UTEM | Página
3

VOLANTINES STRONG | INFORME FINAL
1. Introducción
La digitalización de procesos operativos en la micro, pequeña y mediana empresa
constituye un factor determinante para la eficiencia, la trazabilidad y la
sostenibilidad del negocio. Los modelos artesanales de comercialización,
caracterizados por una alta dependencia de canales informales y de registros
manuales, presentan una capacidad de respuesta limitada frente a fluctuaciones
estacionales de demanda. Cuando el volumen de consultas excede la capacidad
de atención del personal, se producen pérdidas de oportunidad comercial,
degradación del nivel de servicio y una interrupción sistemática de las actividades
productivas.
Volantines Strong, taller dedicado a la manufactura y comercialización de artículos
para la práctica del volantín en la comuna de Cerrillos, opera bajo ese modelo. Su
demanda se concentra en el periodo previo a las Fiestas Patrias, momento en el
cual la atención presencial y la mensajería por Instagram Direct colapsan la
capacidad operativa del fundador. La ausencia de un catálogo digital, de un
registro estructurado de pedidos y de un mecanismo de compra anticipada obliga
a gestionar cada transacción de forma individual y secuencial.
El presente informe documenta el diseño, desarrollo, validación y puesta en
producción de una plataforma web de comercio electrónico con módulo de retiro
en tienda (Click & Collect), construida sobre el framework Django 6.1.3 con Python 3.12+ bajo el
patrón arquitectónico Modelo-Vista-Template, con base de datos relacional
PostgreSQL y una interfaz responsiva orientada a dispositivos móviles. El
documento se estructura conforme al esquema oficial de Informe Final Proyecto SI
y abarca la totalidad de sus dieciocho secciones. El resultado esperado del
proyecto es la reducción de los tiempos de atención, la eliminación del registro
manual de pedidos y la liberación de capacidad productiva en el taller durante la
temporada alta, manteniendo un costo de infraestructura acotado y una operación
autónoma por parte del cliente.
Taller de Sistemas de Información • UTEM | Página
4

VOLANTINES STRONG | INFORME FINAL
2. Descripción General de la Empresa
2.1. Rubro y ubicación de la empresa
Volantines Strong se desempeña en el rubro de manufactura artesanal y
comercialización de artículos deportivos con especialización en insumos y
productos para la práctica del volantín. Su actividad abarca el corte y
adelgazamiento de madera, el ensamblaje de carretes, la preparación de hilos
normalizados y el armado de volantines.
● Dirección operativa: se ubica en Calle Groenlandia 2350, comuna de
Cerrillos, Región Metropolitana, Chile.
● Instalaciones: taller acondicionado con maquinaria de precisión para corte y
pulido, área de ensamblaje manual, zona de empaque y espacio de
atención presencial reducido.
● Cobertura comercial: venta presencial en taller y venta a distancia
coordinada por redes sociales, con entrega exclusiva en el local.
2.2. Productos y servicios
La oferta se organiza en cinco líneas comerciales:
1. Hilos de competencia: hilos curtidos y normalizados conforme a la Ley N°
20.700, en distintas resistencias y metrajes.
2. Carretes: carretes de madera ensamblados y terciados, en capacidades
desde 1.000 hasta 3.0000 yardas.
3. Volantines: unidades de competencia fabricadas en papel de seda y palillos
de bambú adelgazados manualmente, en medidas de 40 × 40 cm y 42 × 42
cm.
4. Maletas de transporte: fundas reforzadas para protección y traslado de
carretes.
5. Accesorios: pegamentos técnicos, palillos de repuesto y protectores de
dedos.
Taller de Sistemas de Información • UTEM | Página
5

VOLANTINES STRONG | INFORME FINAL
La combinación de productos fabricados en taller y artículos preparados para
comercialización exige un control de stock diferenciado por producto terminado,
sin involucrar materias primas.
2.3. Organigrama simplificado de la empresa
Figura 1. Organigrama de la empresa
Taller de Sistemas de Información • UTEM | Página
6

VOLANTINES STRONG | INFORME FINAL
2.3. Problema a abordar
Durante septiembre, la demanda se incrementa de forma severa respecto del
promedio anual. La operación dependía exclusivamente de la atención presencial
y de Instagram Direct, sin catálogo formal ni registro estructurado. Consecuencias
observadas:
● Acumulación superior a 150 mensajes diarios sin respuesta oportuna.
● Tiempos de respuesta de hasta 48 horas para consultas de disponibilidad y
precio.
● Interrupción constante de la manufactura para atender consultas repetitivas.
● Aglomeración de clientes en el taller y coordinación manual de pagos y
entregas.
● Pérdida de ventas por falta de confirmación oportuna de stock.
El problema central es de capacidad y trazabilidad: la empresa no dispone de un
canal transaccional que separe la consulta informativa de la compra efectiva, ni de
un registro único que permita preparar pedidos con anticipación.
2.4. Organización interna
La estructura del equipo de la empresa es dirigida principalmente de forma
individual por el fundador, quien cuenta con el apoyo operativo de su pareja para
labores de ensamblaje manual y tareas de menor complejidad, como el plegado
del papel.
Rol interno Capacidad Funciones principales
Fundador/adminis 1 Dirección comercial, compra de insumos,
trador general manufactura especializada, atención de
clientes y control de ventas.
Asistente 1 Ensamblaje manual de componentes
operativo menores, plegado de papel, empaque y
apoyo logístico.
Tabla 1. Estructura interna.
Taller de Sistemas de Información • UTEM | Página
7

VOLANTINES STRONG | INFORME FINAL
3. Objetivos
3.1. Objetivo General del Proyecto
Implementar una plataforma web de comercio electrónico y gestión de pedidos
para Volantines Strong que automatice el flujo de venta y la coordinación de retiros
bajo la modalidad Click & Collect, reduciendo los tiempos de atención al cliente y
liberando capacidad operativa del taller durante los periodos de alta demanda.
3.2. Objetivos Específicos del Proyecto
1. Digitalizar el catálogo de productos en un portal autogestionable, con
categorías, fichas técnicas, precios e indicador de disponibilidad
actualizables por el administrador sin soporte técnico.
2. Implementar el módulo de compra anticipada (Click & Collect) con
carrito, registro de datos de contacto, confirmación de pago y generación
automática de una orden de preparación codificada para el taller.
3. Desarrollar la herramienta de personalización de carretes en HTML5
Canvas, que permite cargar una imagen, ajustar escala y posición sobre
una plantilla de referencia y previsualizar el resultado antes de la compra.
4. Reducir la dependencia de Instagram como canal transaccional,
derivando la intención de compra a la plataforma web y manteniendo la red
social como canal de difusión y de soporte vía WhatsApp.
5. Garantizar operación estable y responsiva mediante arquitectura MVT
sobre Django, interfaz Mobile-First y pruebas de concurrencia que validen el
comportamiento del sistema en el peak estacional.
Taller de Sistemas de Información • UTEM | Página
8

VOLANTINES STRONG | INFORME FINAL
4. Descripción General del Problema
4.1. Forma actual de resolución del problema
El proceso vigente es reactivo e informal. El cliente consulta por instagram o
acude al taller; el administrador interrumpe la producción para responder, verificar
disponibilidad de forma visual y acordar el pago. La venta se concreta en la
conversación, sin orden de preparación previa ni confirmación documentada. La
entrega se coordina de manera presencial, con el cliente esperando mientras el
pedido se arma.
No existe un punto único de verdad: el stock se conoce por inspección física, los
pedidos se recuerdan o se anotan manualmente y no hay forma de medir cuántas
consultas se transformaron en ventas ni cuántas se perdieron por demora.
4.2. Almacenamiento y Procesamiento de Datos Actual
● Almacenamiento: libretas de papel, notas en el teléfono y conversaciones
de mensajería. Sin base de datos, sin respaldo y sin historial consultable.
● Procesamiento: cálculo manual de totales, verificación visual de stock y
coordinación verbal del retiro.
● Trazabilidad: inexistente. No es posible reconstruir un pedido, auditar una
venta ni analizar la estacionalidad con datos confiables.
● Consecuencias operativas: sobreventa de productos agotados, duplicidad
de pedidos, pérdida de información de contacto y nula capacidad de
generar reportes.
Taller de Sistemas de Información • UTEM | Página
9

VOLANTINES STRONG | INFORME FINAL
4.3. Flujo de Datos Actual y Propuesto
Flujo actual (As-Is). El cliente inicia la interacción por mensajería o de forma
presencial. El administrador recibe la consulta, verifica stock físicamente,
comunica precio y disponibilidad, acuerda el pago y prepara el pedido en el
momento. El dato de la venta queda en la conversación y, eventualmente, en una
nota manual. El flujo es secuencial, depende de una sola persona y no escala con
el volumen de demanda.
Flujo propuesto (To-Be). El cliente accede a la plataforma, navega el catálogo
categorizado, consulta la ficha técnica, personaliza el carrete si corresponde y
agrega productos al carrito. Al confirmar la compra, el sistema registra al cliente,
genera un pedido con código de seguimiento y descuenta stock. El pedido
aparece en el panel de administración con estado Pendiente; el administrador lo
prepara y cambia el estado a Listo para Retiro, lo que habilita la notificación al
cliente por correo. El retiro se ejecuta en el local con el código como identificador.
Toda la operación queda registrada en base de datos y disponible para reportería.
El diagrama completo se encuentra en el Anexo 16.2.1. Figura 2. Diagrama de
flujo actual y 16.2.2. Figura 3. Diagrama de flujo propuesto.
Taller de Sistemas de Información • UTEM | Página
10

VOLANTINES STRONG  |  INFORME FINAL

4.4. Tipos de Usuarios Existentes y Necesarios
| Perfil  | Situación actual  |     | Requerimiento en el sistema  |     |
| ------- | ----------------- | --- | ---------------------------- | --- |
Cliente  Consulta por Instagram o  Navegación  autónoma  del
comprador  acude  al  taller;  sin  catálogo,  ficha  técnica,
|     | catálogo    | ni  precios  | carrito, pago y confirmación  |     |
| --- | ----------- | ------------ | ----------------------------- | --- |
|     | publicados  | de  forma    | de retiro.                    |     |
estable.
Administrador  Responde  consultas,  Panel  único  para gestionar
del taller  verifica  stock  y  prepara  productos, stock, pedidos y
|     | pedidos de forma manual  |     | estados,       | con  operación  |
| --- | ------------------------ | --- | -------------- | --------------- |
|     | y simultánea.            |     | simplificada.  |                 |
Visitante  no  No existe como categoría  Acceso  a  catálogo  y
| registrado  | diferenciada.  |     | personalizador  | sin  registro;         |
| ----------- | -------------- | --- | --------------- | ---------------------- |
|             |                |     | registro        | obligatorio  solo  al  |
confirmar compra.
Tabla 2. Tipos de usuarios existentes.
4.5. Diagrama de Flujo del Proceso
El diagrama completo del flujo de proceso se encuentra en el Anexo 16.2.3. Figura
4. Diagrama de flujo del proceso, donde se detalla el proceso de compra y venta.

Taller de Sistemas de Información • UTEM | Página

11

VOLANTINES STRONG | INFORME FINAL
5. Toma de Requerimientos
5.1. Requerimientos Funcionales
RF-01. Visualización del catálogo: El sistema debe permitir visualizar un catálogo
de productos completo, organizado e intuitivo.
RF-02. Clasificación por categorías: El catálogo debe clasificar el producto en
categorías, tales como maletas, carretes, hilos, volantines y accesorios.
RF-03. Ficha técnica de producto: Cada producto debe disponer de una ficha
individual con su descripción y especificaciones técnicas, como medidas,
materiales y resistencia.
RF-04. Carrito de compras: El sistema debe incorporar un carrito de compras que
permite agregar, eliminar y modificar productos.
RF-05. Procesamiento de pagos: La plataforma debe permitir informar el pago
mediante transferencia bancaria y adjuntar el comprobante correspondiente, que
será revisado por el administrador antes de confirmar el pedido. No se incorpora
una pasarela de pago automática dentro de este alcance.
RF-06. Orden de preparación: Una vez confirmada la compra, el sistema debe
generar automáticamente una orden de preparación del pedido con detalle del
pedido.
RF-07. Integración con WhatsApp: La plataforma debe contar con un enlace
directo a WhatsApp para facilitar la atención de consultas.
RF-08. Enlaces a redes sociales: La plataforma debe contar con enlaces a las
redes sociales del negocio, especialmente Instagram.
RF-09. Personalización de carretes: El sistema debe contener una herramienta de
personalización interactiva que permita cargar una imagen y visualizar cómo se
vería aplicada sobre la superficie de un carrete de referencia.
Taller de Sistemas de Información • UTEM | Página
12

VOLANTINES STRONG | INFORME FINAL
5.2. Requerimientos No Funcionales
RNF-01. Estabilidad de desempeño: El sistema debe mantener un funcionamiento
estable y eficiente.
RNF-02. Concurrencia: La plataforma debe soportar una alta concurrencia de
usuarios durante los periodos de mayor demanda, especialmente en septiembre.
RNF-03. Responsividad: La interfaz debe ser responsiva y adaptarse a distintos
dispositivos y tamaños de pantalla, priorizando la navegación desde teléfonos
móviles.
RNF-04. Seguridad: El sistema debe garantizar la seguridad y confidencialidad de
datos personales y de la información de los clientes.
RNF-05. Usabilidad: La experiencia del usuario debe ser intuitiva, accesible y
sencilla.
RNF-06. Disponibilidad: La plataforma debe mantener una disponibilidad
adecuada para que los usuarios consulten productos y realicen compras sin
interrupciones.
6. Alcance y Limitaciones del Proyecto
6.1. Alcance
El alcance define exactamente qué funcionalidades, tecnologías y procesos serán
cubiertos por el sistema. Para este proyecto, se divide en las siguientes áreas:
● Alcance Funcional: Desarrollo de una plataforma web con un catálogo
digital permanente y categorizado (maletas, carretes, hilos, volantines y
accesorios). Incluye un carrito de compras automatizado, logística de
compra anticipada con retiro en el local (Click & Collect), y una herramienta
gráfica interactiva para previsualizar el diseño de carteles personalizados.
Taller de Sistemas de Información • UTEM | Página
13

VOLANTINES STRONG | INFORME FINAL
● Alcance Técnico: Construcción de una aplicación web bajo el patrón
Modelo-Vista-Template (MVT) utilizando el framework Django y una base de
datos relacional. El diseño de la interfaz será responsivo, priorizando la
navegación desde teléfonos móviles (Mobile-First) para captar el tráfico
proveniente de redes sociales.
● Alcance Operativo: Implementación de un panel de administración cerrado
y autogestionable. Esto permitirá al dueño del taller en Cerrillos actualizar
descripciones, especificaciones técnicas (medidas, resistencia), controlar el
stock de productos terminados y gestionar el cambio de estado de los
pedidos recibidos.
● Alcance de Integración: Conexión de la plataforma con enlaces directos a
las redes sociales del negocio (Instagram) y redirección a WhatsApp para
consultas o soporte técnico.
6.2. Limitaciones
Las limitaciones establecen las fronteras del proyecto, aclarando qué elementos
quedan fuera de la responsabilidad del sistema o del equipo de desarrollo:
● Limitaciones Logísticas: El sistema excluye completamente la gestión,
cálculo de tarifas o coordinación de despachos a domicilio mediante flotas
de transporte. Toda la logística de entrega está restringida al retiro
presencial en el local.
● Limitaciones de Inventario y Producción: El software no contempla el
control de inventario de las materias primas utilizadas en el taller (como
madera, hilo crudo o pegamento) ni la gestión de los procesos internos de
manufactura artesanal. Solo contabilizará el stock de productos finales
listos para la venta.
● Limitaciones de Plataforma: El desarrollo se enfoca exclusivamente en
una aplicación web accesible mediante navegadores. Queda excluida la
programación de aplicaciones móviles nativas descargables desde App
Store o Google Play.
Taller de Sistemas de Información • UTEM | Página
14

VOLANTINES STRONG | INFORME FINAL
● Limitaciones Contables y Tributarias: En esta fase del proyecto, el
sistema no incluye integración directa con la API del Servicio de Impuestos
Internos (SII) para la emisión y facturación electrónica automática de
boletas.
● Limitaciones de Tiempo y Recursos: El alcance de construcción, pruebas
de calidad y despliegue está estrictamente acotado a los plazos del
semestre académico de la asignatura Taller de sistemas de información,
contando únicamente con la capacidad operativa de los 5 integrantes del
equipo de proyecto.
● De infraestructura: el entorno de producción opera en un plan acotado de
cloud, con escalamiento limitado y sujeto a la política del proveedor.
7. Organización del Grupo Proyecto
7.1. Estructura de toma de decisiones y distribución de trabajo
Las decisiones de arquitectura se adoptan por consenso técnico entre Backend y
Frontend, con validación de viabilidad de negocio por parte de la Product Owner.
La priorización del backlog se revisa al cierre de cada iteración. El trabajo se
distribuye en un tablero Kanban con columnas Backlog, En Análisis, En Desarrollo,
En Revisión y Terminado, aplicando un límite de trabajo en progreso de tres tareas
por sub-equipo para reducir el Lead Time y evitar multitarea.
Las reuniones de sincronización se realizan dos veces por semana, con una
revisión de avance semanal y una sesión de planificación al inicio de cada
iteración. Las decisiones que afectan alcance, costo o fecha se registran en
minuta y requieren acuerdo explícito del equipo.
Taller de Sistemas de Información • UTEM | Página
15

VOLANTINES STRONG | INFORME FINAL
7.2. Roles y responsabilidades de cada integrante
1. Product Owner — Javiera Flores: define y prioriza las funcionalidades del
Product Backlog, como el módulo Click & Collect y el catálogo. Representa los
intereses del negocio Volantines Strong.
2. Scrum Master — Juan Pablo Vega Pinto: facilita las reuniones de
sincronización, promueve el cumplimiento de la metodología de trabajo, supervisa
los límites de trabajo en progreso (WIP) en el tablero Kanban y ayuda a resolver
bloqueos del equipo.
3. Analista QA — Juan Pablo Vega Pinto: realiza pruebas de calidad del sistema,
incluyendo pruebas de integración y de responsividad web.
4. Backend Developer — Edmundo Enrique Moya Creo: desarrolla la arquitectura
del servidor y la base de datos, además de la gestión del carrito de compras y la
emisión de órdenes de preparación para el retiro en el local.
5. Frontend Developer — Christian Jesús Torres Jeldres: programa la interfaz de
usuario, implementa la visualización del catálogo y procura que el sistema sea
responsivo y adaptable a dispositivos móviles.
6. Analista funcional — Pedro Nicolás Saravia Abuhadba: analiza las
necesidades del negocio y de los usuarios, y las traduce en requerimientos y
funcionalidades que orientan el desarrollo del sistema.
7. Encargado de calidad — Pedro Nicolás Saravia Abuhadba: revisa la
consistencia y calidad de los entregables del proyecto, verificando que la
documentación y los productos de trabajo se ajusten a los criterios definidos por el
equipo.
Taller de Sistemas de Información • UTEM | Página
16

VOLANTINES STRONG | INFORME FINAL
8. Fases del Proyecto
8.1. Fase 0 Lanzamiento
Objetivo: establecer el problema, el alcance preliminar y las condiciones de
ejecución.
Actividades realizadas: entrevistas con el fundador en el taller de Cerrillos para
levantar el proceso actual y cuantificar la demanda estacional. Definición del
problema, alcance preliminar y restricciones del proyecto. Constitución del equipo
y asignación de roles Scrumban. Elaboración del acta de inicio y del backlog inicial
de historias de usuario. Definición de la línea base de métricas: tiempo de
respuesta, pedidos diarios y volumen de consultas.
Evidencias: actas de inicio, minutas de reunión, backlog inicial priorizado y
registro de métricas de línea base.
8.2. Fase 1: Diseño e implementación
Objetivo: especificar la solución y preparar la base técnica del desarrollo.
Actividades realizadas: levantamiento detallado de requerimientos funcionales y
no funcionales. Diseño de la arquitectura MVT y definición de la estructura de
aplicaciones Django. Modelamiento conceptual y físico de la base de datos,
incluido el proceso de normalización a 3FN. Elaboración de wireframes y flujo de
navegación Mobile.First. Configuración del repositorio, estándares de código y
tablero Kanban.
Evidencias: diagrama entidad-relación, esquema físico SQL, documento de
normalización, wireframes de catálogo, ficha de producto, carrito y panel
administrativo, repositorio inicializado con estructura del proyecto.
Taller de Sistemas de Información • UTEM | Página
17

VOLANTINES STRONG | INFORME FINAL
8.3. Fase 2: Desarrollo y producción.
Objetivo: construir y desplegar las funcionalidades comprometidas.
Actividades realizadas: implementación de modelos ORM, migraciones y datos
de prueba. Desarrollo de vistas del catálogo, ficha de producto, carrito y checkout.
Implementación de módulo Click & Collect con generación de código de
seguimiento. Desarrollo del personalizador gráfico en HTML5 Canvas con carga,
escalado y explotación de vista previa. Configuración del panel administrativo,
permisos y cambio de estados de pedido. Integración de enlaces a WhatsApp e
Instagram. Despliegue en entorno de staging.
Evidencias: repositorio con historial de commits y pull requests aprobados, base
de datos poblada, módulo Canvas operativo, entorno de staging accesible y panel
administrativo configurado.
8.4. Fase 3: Validación.
Objetivo: verificar el cumplimiento de requerimientos y la estabilidad operativa.
Actividades realizadas: pruebas unitarias sobre modelos, carrito y cálculo de
totales. Pruebas de integración del flujo completo de compra y generación de orden.
Pruebas de usabilidad y responsividad en dispositivos móviles reales y distintos
navegadores. Pruebas de carga con 120 usuarios concurrentes simulados. Corrección
de defectos y revalidación.
Evidencias: informe de resultados QA, matriz de trazabilidad requerimiento-prueba,
registro de defectos y evidencia de corrección, reporte de pruebas de carga.
Taller de Sistemas de Información • UTEM | Página
18

VOLANTINES STRONG | INFORME FINAL
8.5. Fase Post: Evaluación e informes finales
Objetivo: poner el sistema en producción, transferir conocimiento y cerrar el
proyecto.
Actividades realizadas: despliegue a producción en Render con base de datos
PostgreSQL. Mitigación de datos iniciales de catálogo y stock. Capacitación
presencial al fundador en gestión de productos, stock y pedidos. Entrega de
manual de usuario y del plan de continuidad. Elaboración del informe final y de la
presentación de cierre.
Evidencias: URL de producción activa, manual de usuario, acta de capacitación,
informe final y presentación.
9. Diseño del Sistema
9.1. Metodología utilizada
Para la gestión y desarrollo del proyecto se utiliza la metodología ágil Scrumban,
combinando las ceremonias y roles estructurados de Scrum con el flujo de trabajo
continuo y la visualización de Kanban. Esta metodología es idónea para el
proyecto ya que permite:
● Administrar el trabajo a través de un tablero Kanban visual, controlando los
límites de trabajo en progreso (WIP) para evitar cuellos de botella en el
desarrollo.
● Mantener los roles definidos (Product Owner, Scrum Master y equipo de
desarrollo).
● Utilizar métricas continuas como el Lead Time y Cycle Time para evaluar la
eficiencia de la entrega de funcionalidades, priorizando los requerimientos
más urgentes del Product Backlog, como el catálogo y el módulo de Click &
Collect.
Taller de Sistemas de Información • UTEM | Página
19

VOLANTINES STRONG  |  INFORME FINAL

9.2. Requerimientos del sistema
Software utilizado
| Componente              | Tecnología  | Versión/uso                 |     |
| ----------------------- | ----------- | --------------------------- | --- |
| Lenguaje backend        | Python      | 3.11                        |     |
| Framework web           | Django      | 5.2 LTS, patrón MVT         |     |
| Base de datos           | PostgreSQL  | 15, relacional              |     |
| Servidor de aplicación  | Gunicorn    | Producción                  |     |
| Frontend                | HTML5,      | CSS3,  Interfaz responsiva  |     |
JavaScript, ES6.
| Estilos               | Bootstrap adaptado  | Grilla y componentes  |          |
| --------------------- | ------------------- | --------------------- | -------- |
| Control de versiones  | Git/GitHub          | Repositorio           | y  pull  |
requests
| Gestión de trabajo  | GitHub Projects  | Tablero Kanban        |     |
| ------------------- | ---------------- | --------------------- | --- |
| Alojamiento         | Render           | Producción y staging  |     |
Tabla 3. Software utilizado.

Taller de Sistemas de Información • UTEM | Página

20

VOLANTINES STRONG | INFORME FINAL
Sistema operativo y hardware requerido
Entorno Especificación mínima
Servidor de producción Linux Ubuntu 22.04 LTS 64-bit, 1vCPU,
1 GB RAM, 10 GB SSD
Equipo de desarrollo 4 GB RAM, 20 GB de espacio libre,
Python 3.11 y PostgreSQL local
Cliente Navegador actualizado en android,
iOS, windows o macOS; resolución
mínima 320px
Tabla 4. Sistema Operativo y hardware requerido.
9.3. Modelo Entidad-Relación
El modelo conceptual representa las entidades necesarias para sostener el
catálogo, la
identidad del comprador y el ciclo de vida del pedido. Se utiliza notación Chen
extendida: rectángulos para entidades, elipses para atributos, rombos para
relaciones y cardinalidades expresadas como (mínimo, máximo). Los atributos
identificadores se subrayan y las claves foráneas se indican con la entidad de
origen.
Taller de Sistemas de Información • UTEM | Página
21

VOLANTINES STRONG | INFORME FINAL
Figura 4. Diagrama Entidad-Relación
9.4. Modelo Físico-Relacional
El modelo físico traduce el modelo conceptual a estructuras PostgreSQL. Se
adoptan las siguientes convenciones:nombres en minúscula y singular, claves
primarias sustitutas de tipo entero autoincremental, claves foráneas con el mismo
nombre de la clave referenciada, restricciones CHECK para dominios acotados y
acciones referenciales explícitas.
Taller de Sistemas de Información • UTEM | Página
22

VOLANTINES STRONG | INFORME FINAL
Figura 5. Modelo Físico-Relacional
9.5. Modelo Físico-Relacional Normalizado (1FN, 2FN y 3FN)
La normalización se aplicó de forma progresiva sobre el esquema inicial, con el
objetivo de eliminar redundancia, evitar anomalías de inserción, actualización y
borrado, y garantizar que cada hecho se almacene una sola vez (Pressman,
2015). El proceso se documenta a continuación.
Taller de Sistemas de Información • UTEM | Página
23

VOLANTINES STRONG | INFORME FINAL
Figura 6. Modelo Físico-Relacional Normalizado
10. Desarrollo del Sistema
El proceso de construcción abarca la programación del módulo de compra
anticipada (Click & Collect), diseñando un carrito de compras dinámico que calcula
los totales y genera una orden estructurada para el equipo del taller. Se configura
el panel de administración autogestionable de Django, permitiendo al dueño de
Volantines Strong actualizar el inventario y características técnicas sin depender
de terceros. Adicionalmente, se desarrolla el visualizador interactivo donde el
usuario puede previsualizar cómo quedarán sus imágenes aplicadas en los
carretes de referencia antes de confirmar la compra.
Taller de Sistemas de Información • UTEM | Página
24

VOLANTINES STRONG  |  INFORME FINAL

10.1. Login y autenticación
La autenticación se apoya en el subsistema nativo de Django. Las credenciales se
validan contra un hash PBKDF2-SHA256 y la sesión se gestiona mediante cookies
firmadas con  atributos HttpOnly y Secure en producción. Todos los formularios
incorporan  token  CSRF  y  las vistas administrativas verifican los  permisos del
usuario  antes  de  ejecutar  acciones.  El  acceso  público  al  catálogo  y  al
personalizador  no requiere autenticación. El  registro se solicita al confirmar la
compra,  momento  en  que  se  capturan  nombre,  correo  y  teléfono  para  la
coordinación del retiro.
10.2. Niveles de acceso y acciones de usuarios
| Nivel  | Rol        | Acciones permitidas  |            |            |          |         |
| ------ | ---------- | -------------------- | ---------- | ---------- | -------- | ------- |
| 1      | Visitante  | Navegar              | catálogo,  |            | filtrar  | por     |
|        |            | categoría,           |            | consultar  |          | fichas  |
técnicas, usar el personalizador y
|     |     | agregar  | productos  |     | al  carrito  | de  |
| --- | --- | -------- | ---------- | --- | ------------ | --- |
sesión.
| 2   | Cliente registrado  | Todo  lo   | anterior, más confirmar  |     |               |     |
| --- | ------------------- | ---------- | ------------------------ | --- | ------------- | --- |
|     |                     | pedidos,   | registrar                |     | datos         | de  |
|     |                     | contacto,  | pagar                    |     | y  consultar  | el  |
estado de sus pedidos mediante
código de seguimiento.
| 3   | Administrador  | Acceder al panel, crear y editar  |     |           |     |          |
| --- | -------------- | --------------------------------- | --- | --------- | --- | -------- |
|     |                | productos,                        |     | ajustar   |     | stock,   |
|     |                | consultar                         |     | pedidos,  |     | cambiar  |
estados y emitir reportes.
El principio aplicado es de mínimo privilegio: el rol administrativo no se asigna por
registro  público,  sino  por  configuración  directa  en  el  panel,  y  las  acciones
sensibles quedan registradas con usuario y fecha.
Taller de Sistemas de Información • UTEM | Página

25

VOLANTINES STRONG | INFORME FINAL
10.3. Vistas del sistema
Catálogo general: Grilla responsiva con imagen, nombre, precio y disponibilidad.
Incluye filtro por categoría y ordenamiento por precio y nombre. En móvil se
presenta en una columna con tarjetas de altura uniforme.
Ficha de producto: Detalle con descripción, medidas, material, resistencia y
stock. Presenta el selector de cantidad y el acceso al personalizador cuando el
producto lo admite.
Personalizador de carretes: Interfaz basada en HTML5 Canvas. El usuario carga
una imagen, ajusta escala, rotación y posición sobre una plantilla de carrete, y
obtiene una previsualización. La vista previa se exporta como imagen y se asocia
a la línea del pedido.
Carrito y checkout: Resumen de líneas con edición de cantidad y eliminación,
cálculo de subtotal y total, formulario de datos de contacto, selección de fecha de
retiro y confirmación. Al confirmar, se muestra el código de seguimiento y las
instrucciones de retiro.
Panel administrativo: Listado de pedidos con filtro por estado, detalle de ítems,
cambio de estado y acceso al ajuste de stock. Incluye la gestión del catálogo con
vista previa de publicación.
10.4. Reportes del sistema
1. Pedidos por estado: volumen y monto agregado por estado, con el
objetivo de dimensionar la carga de preparación pendiente.
2. Ventas por categoría: distribución de unidades y montos por línea de
producto, para identificar rotación y apoyar la reposición.
3. Retiros programados: consolidado de pedidos listos por fecha y franja
horaria, para organizar la preparación física y evitar aglomeraciones en el
local.
4. Ganancias mensuales: resumen de ingresos y ganancias por mes, con comparación
respecto del mes anterior y del mismo mes del año anterior. La ganancia se calcula
con el costo unitario registrado al momento de la venta.
5. Exportación a Excel: genera un archivo con hojas de resumen mensual, pedidos,
detalle por producto y categorías, considerando todos los pedidos del rango de
fechas seleccionado.
Los reportes se generan a partir de consultas agregadas sobre el esquema
normalizado y se presentan en el panel con filtros por rango de fechas.
Taller de Sistemas de Información • UTEM | Página
26

VOLANTINES STRONG  |  INFORME FINAL

11. Análisis de Riesgos
11.1. Riesgos identificados
| ID  Categoría  | Descripción  | Prob.  | Impacto  | Momento  | de  |
| -------------- | ------------ | ------ | -------- | -------- | --- |
exposición
R-01  Tecnológico  Saturación  de  la  Alta  Alto  Producción
infraestructura
por  concurrencia
elevada
durante
septiembre.
R-02  Tecnológico  Agotamiento  del  Media  Alto  Validación  y
|     | pool        | de     |     | producción  |     |
| --- | ----------- | ------ | --- | ----------- | --- |
|     | conexiones  | a      |     |             |     |
|     | base  de    | datos  |     |             |     |
bajo carga.
| R-03  Operacional  | Desfase            | entre  Media  | Alto  | Operación  |     |
| ------------------ | ------------------ | ------------- | ----- | ---------- | --- |
|                    | stock  físico      | y             |       |            |     |
|                    | stock  registrado  |               |       |            |     |
en la plataforma.
| R-04  Operacional  | Error           | de  Media  | Medio  | Operación  |     |
| ------------------ | --------------- | ---------- | ------ | ---------- | --- |
|                    | digitación      | en         |        |            |     |
|                    | precios         | o          |        |            |     |
|                    | especificación  | es         |        |            |     |
|                    | por  parte      | del        |        |            |     |
administrador.
Taller de Sistemas de Información • UTEM | Página

27

VOLANTINES STRONG  |  INFORME FINAL

| R-05  Adopción  | Resistencia  | de  Media  | Medio  | Lanzamiento  |
| --------------- | ------------ | ---------- | ------ | ------------ |
clientes
habituales a
abandonar
|     | Instagram  | como  |     |     |
| --- | ---------- | ----- | --- | --- |
canal de compra.
R-06  Adopción  Baja  apropiación  Media  Alto  Post-producci
|     | del  | panel  |     | ón  |
| --- | ---- | ------ | --- | --- |
administrativo por
|     | parte  | del  |     |     |
| --- | ------ | ---- | --- | --- |
fundador.
| R-07  Seguridad  | Fuga          | o  Baja  | Alto  | Producción  |
| ---------------- | ------------- | -------- | ----- | ----------- |
|                  | intercepción  | de       |       |             |
datos  personales
de contacto.
| R-08  Seguridad  | Intentos   | de  Baja  | Alto  | Producción  |
| ---------------- | ---------- | --------- | ----- | ----------- |
|                  | inyección  | SQL  o    |       |             |
|                  | ejecución  | de        |       |             |
|                  | scripts    | en        |       |             |
formularios.
| R-09  Proyecto  | Desviación   | de  Medida  | Medio  | Desarrollo  |
| --------------- | ------------ | ----------- | ------ | ----------- |
|                 | plazo        | por         |        |             |
|                 | complejidad  | del         |        |             |
personalizador
gráfico.

Taller de Sistemas de Información • UTEM | Página

28

VOLANTINES STRONG  |  INFORME FINAL

11.2. Planes de mitigación
| Riesgo  | Medida preventiva  |     |     | Medida correctiva   |     |
| ------- | ------------------ | --- | --- | ------------------- | --- |
R-01  Optimización  de  consultas  con  Escalamiento  temporal
select_related  y  prefetch_related,  del  plan  de  hosting  y
caché  de  vistas  y  monitoreo  de  activación  de  página de
|     | latencia.  |     |     | contingencia.  |     |
| --- | ---------- | --- | --- | -------------- | --- |
R-02  Configuración  de  CONN_MAX_AGE,  Reinicio  controlado  del
uso de PgBouncer y pruebas de carga  pool  y  ajuste  de  límites
|     | previas al despliegue.  |     |     | de conexión.  |     |
| --- | ----------------------- | --- | --- | ------------- | --- |
R-03  Reserva temporal de stock durante el  Anulación de pedido con
checkout y alerta de stock mínimo.  notificación  al  cliente  y
ofrecimiento  de
sustitución.
R-04  Validaciones de formulario,  Reversión  del  cambio  y
Confirmación previa a la publicación y  comunicación  inmediata
|     | registro de cambios.  |     |     | a clientes afectados.  |     |
| --- | --------------------- | --- | --- | ---------------------- | --- |

R-05  Campaña  de  derivación  desde  Atención  asistida  por
|     | Instagram,  | enlaces  | directos  | y  WhatsApp  | para  clientes  |
| --- | ----------- | -------- | --------- | ------------ | --------------- |
comunicación del beneficio de compra  que no logren completar
|     | anticipada.  |     |     | la compra.  |     |
| --- | ------------ | --- | --- | ----------- | --- |
R-06  Capacitación  presencial,  manual  de  Sesión  de  refuerzo  y
|     | usuario               | y  panel  | simplificado  | con  soporte  | de  segundo  |
| --- | --------------------- | --------- | ------------- | ------------- | ------------ |
|     | acciones de un clic.  |           |               | nivel.        |              |

Taller de Sistemas de Información • UTEM | Página

29

VOLANTINES STRONG | INFORME FINAL
R-07 HTTPS obligatorio, hash de Rotación de
credenciales y minimización de datos credenciales,
almacenados. revocación de sesiones y
notificación.
R-08 Uso del ORM, validación de Bloqueo de origen,
entradas y protección CSRF. revisión de logs y parche
de seguridad.
R-09 Priorización del backlog y prototipo Reasignación de horas
temprano del personalizado. desde tareas de menor
prioridad.
11.3. Conclusiones sobre riesgos
Los riesgos de mayor severidad se concentran en la operación de temporada alta
y en la adopción por parte del usuario administrador. Ambos fueron abordados
antes del despliegue: el primero mediante pruebas de carga y optimización de
consultas; el segundo mediante capacitación y simplificación del panel. Los
riesgos de seguridad se mitigaron con controles estándar del framework y
configuración de producción. No se materializó ningún riesgo crítico durante la
puesta en marcha.
Taller de Sistemas de Información • UTEM | Página
30

VOLANTINES STRONG  |  INFORME FINAL

12. Manejo de Crisis
12.1. Problemas que generaron crisis
Fallas  del  Servidor:  En  caso  de  caída  de  la  plataforma  por  alto tráfico, se
implementará un  protocolo de auto-escalamiento temporal en el hosting. Si el
sistema  colapsa  completamente,  se  activará  una  página  estática  de
mantenimiento que redirigirá automáticamente a los clientes al canal de atención
por WhatsApp para no frenar las ventas.
Contingencia Operativa: Ante inconsistencias de stock, el administrador contará
con una función rápida para anular pedidos y notificar instantáneamente al cliente
para ofrecer sustituciones.
Incidentes  de  Datos:  Restauración  inmediata  a  partir  del  último  respaldo
automatizado de la base de datos y reseteo preventivo de sesiones de usuario.
12.2. Tiempo y acciones de solución
| Crisis                | Tiempo de resolución  | Acciones ejecutadas         |     |     |
| --------------------- | --------------------- | --------------------------- | --- | --- |
| Conexiones a base de  | 4 horas               | Incorporación de PgBouncer  |     |     |
| datos                 |                       | como                        |     |     |
concentrador, ajuste de
CONN_MAX_AGE, cierre de
|     |     | conexiones  | inactivas       | y   |
| --- | --- | ----------- | --------------- | --- |
|     |     | repetición  | de  la  prueba  | de  |
carga.
| Almacenamiento  | 6 horas  | .Migración de archivos a    |     |     |
| --------------- | -------- | --------------------------- | --- | --- |
| multimedia      |          | almacenamiento externo S3,  |     |     |
|                 |          | actualización               |     | de  |
|                 |          | configuración               |     | de  |
MEDIA_ROOT y revalidación
|     |     | de  carga  | y recuperación de  |     |
| --- | --- | ---------- | ------------------ | --- |
imágenes.
Taller de Sistemas de Información • UTEM | Página

31

VOLANTINES STRONG | INFORME FINAL
12.3. Efectos colaterales y replanificación
La resolución de ambas crisis consumió diez horas adicionales del Backend
Developer durante la semana once. El impacto se absorbió con la holgura del
Sprint 8 y con la postergación de dos días en la entrega de los reportes analíticos
del panel. No se modificó la fecha de entrega final ni el alcance comprometido.
Como efecto positivo, el incidente derivó en la incorporación de pruebas de carga
al cierre de cada iteración y en la externalización definitiva de archivos estáticos y
multimedia.
13. Plan de Trabajo
13.1. Cronograma de actividades
La ejecución del proyecto se organiza en Sprints iterativos dentro de las fases
definidas:
1. Fase 0 y 1 (Diseño e Implementación): Modelado de la base de datos,
levantamiento del servidor backend en Django y diseño de las vistas
móviles.
2. Fase 2 (Desarrollo):
○ Integración del catálogo autogestionable y carrito de compras.
○ Desarrollo del módulo Click & Collect para programar los retiros.
○ Integración de la herramienta de personalización gráfica de los
carretes.
3. Fase 3 (Validación): Ejecución de pruebas de calidad (QA), enfatizando
pruebas de integración, estabilidad transaccional y responsividad móvil en
distintos navegadores.
4. Fase Post (Producción): Despliegue a la nube, migración de enlaces en el
perfil de Instagram y entrega de documentación.
Taller de Sistemas de Información • UTEM | Página
32

VOLANTINES STRONG  |  INFORME FINAL

13.2. Plan estimado vs real
| Fase    | Horas       | Horas   | Desviación  | Causa        |               |     |
| ------- | ----------- | ------- | ----------- | ------------ | ------------- | --- |
|         | estimación  | reales  |             |              |               |     |
| Fase 0  | 40          | 42      | +2          | Entrevistas  | adicionales   | y   |
|         |             |         |             | validación   | de  métricas  | de  |
línea base.
| Fase 1  | 60  | 58  | -2  | Mayor  | eficiencia  | en  el  |
| ------- | --- | --- | --- | ------ | ----------- | ------- |
modelamiento del DER.
| Fase 2  | 160  | 172  | +12  | Complejidad  |     | del  |
| ------- | ---- | ---- | ---- | ------------ | --- | ---- |
personalizador en Canvas y
ajustes de responsividad.
| Fase 3  | 80  | 88  | +8  | Resolución  | de  la  | crisis de  |
| ------- | --- | --- | --- | ----------- | ------- | ---------- |
conexiones y repetición de
pruebas.
| Fase   | 40   | 38   | -2   | Automatización               |      | del     |
| ------ | ---- | ---- | ---- | ---------------------------- | ---- | ------- |
| Post   |      |      |      | despliegue en Render.        |      |         |
| Total  | 380  | 398  | +18  | Desviación global del 4,7%,  |      |         |
|        |      |      |      | dentro                       | del  | margen  |
aceptable.

Taller de Sistemas de Información • UTEM | Página

33

VOLANTINES STRONG  |  INFORME FINAL

13.3. Responsables por tareas
| Fase       |     |     | Responsable principal  |       | Apoyo                          |     |
| ---------- | --- | --- | ---------------------- | ----- | ------------------------------ | --- |
| Fase 0     |     |     | Javiera Flores         |       | Pedro Saravia                  |     |
| Fase 1     |     |     | Edmundo Moya           |       | Christian Torres               |     |
| Fase 2     |     |     | Edmundo                | Moya  | y  Javiera Flores (validación  |     |
|            |     |     | Christian Torres       |       | funcional)                     |     |
| Fase 3     |     |     | Juan Pablo Vega        |       | Equipo completo                |     |
| Fase Post  |     |     | Edmundo Moya           |       | Equipo completo                |     |
13.4. Costos en tiempo y dinero
| Ítem         |     | Estimado (CLP)  |     | Real (CLP)  | Variación   |             |
| ------------ | --- | --------------- | --- | ----------- | ----------- | ----------- |
| Honorarios   |     | de  0           |     | 0           | Convenio    | académico,  |
| consultoría  |     |                 |     |             | sin  costo  | para  el    |
cliente.
| Alojamiento  |           | cloud  60.000  |     | 506.000  | Ahorro por facturación  |     |
| ------------ | --------- | -------------- | --- | -------- | ----------------------- | --- |
| (plan        | inicial,  | 4              |     |          | mensual.                |     |
meses)
| Dominio web .cl  |     | 11.000  |     | 9.950  | Registro anual en NIC  |     |
| ---------------- | --- | ------- | --- | ------ | ---------------------- | --- |
Chile.
| Almacenamiento  |     | 15.000  |     | 0   | Uso  de         | capa  gratuita  |
| --------------- | --- | ------- | --- | --- | --------------- | --------------- |
| externo         |     | de      |     |     | del proveedor.  |                 |
multimedia
| total      | inversión  | 86.000  |     | 65.950  | Ahorro    | de  20.050  |
| ---------- | ---------- | ------- | --- | ------- | --------- | ----------- |
| monetaria  |            |         |     |         | (23,3%).  |             |
Taller de Sistemas de Información • UTEM | Página

34

VOLANTINES STRONG | INFORME FINAL
13.5. Estado del proyecto en la entrega final
El proyecto se encuentra desplegado en Vercel
(https://volantines-strong.vercel.app) y utiliza Supabase como base de datos y
almacenamiento de archivos. El catálogo, el carrito, el checkout con comprobante
de transferencia, el panel administrativo, el personalizador de carretes y los
reportes avanzados están implementados, validados con 28 pruebas automáticas y
publicados. El build de Vercel aplica las migraciones y recolector de archivos
estáticos; las variables de Storage y correo quedaron configuradas en el
proyecto. La integración de una pasarela de pago automática permanece fuera del
alcance comprometido; el flujo oficial es transferencia bancaria con revisión
manual del comprobante. Queda como tarea de operación verificar el dominio de
remitente en Resend para asegurar la entrega de los correos reales.
Taller de Sistemas de Información • UTEM | Página
35

VOLANTINES STRONG  |  INFORME FINAL

14. Plan de Continuidad y Riesgos Post Producción
14.1. Principales riesgos posteriores a la implementación
| ID  Riesgo  | Descripción  |     | Impacto operativo  |     |
| ----------- | ------------ | --- | ------------------ | --- |
P-01  pérdida de credenciales  El administrador olvida o  Imposibilidad  de
|     | extravía sus accesos al  |     | gestionar  | pedidos  |
| --- | ------------------------ | --- | ---------- | -------- |
|     | panel.                   |     | y stock.   |          |
P-02  crecimiento de dato  Acumulación de pedidos  Degradación
|     | históricos                |     | sin  progresiva  | del  |
| --- | ------------------------- | --- | ---------------- | ---- |
|     | depuración ni archivado.  |     | renacimiento.    |      |
P-03  cambios  de  la  API  de  Modificación  de  Interrupción  de
| WhatsApp  | parámetros  | o  políticas  | notificaciones  | al  |
| --------- | ----------- | ------------- | --------------- | --- |
|           | de la API.  |               | cliente.        |     |
P-04  Falta  de  actualización  El  administrador  no  Sobreventa  y
| de stock  | registra      |     | ventas  reclamos.  |     |
| --------- | ------------- | --- | ------------------ | --- |
|           | presenciales  | en  | la                 |     |
plataforma.
P-05  Dependencia  de  un  Solo el fundador conoce  Riesgo  operativo
| único responsable  | la operación del panel.  |     | ante  | ausencia  |
| ------------------ | ------------------------ | --- | ----- | --------- |
prolongada.
P-06  Vencimiento  de  Dominio,  certificado  o  Caída  del  sitio  y
| servicios  | plan  de     | hosting  | sin  pérdida  | de  |
| ---------- | ------------ | -------- | ------------- | --- |
|            | renovación.  |          | continuidad.  |     |
14.2. Implicaciones en las operaciones
Una interrupción durante septiembre obligaría a retornar al modelo manual de
Instagram, reactivando los tiempos de respuesta prolongados y la saturación del
taller.  La  pérdida  de  historial  afectaría  la  capacidad  de  auditar  pedidos y  de
analizar  demanda.  La  falta  de  actualización  de  stock  generaría  sobreventa y
deterioro de la confianza del cliente.

Taller de Sistemas de Información • UTEM | Página

36

VOLANTINES STRONG | INFORME FINAL
14.3. Plan de mantenimiento y mitigación
Capacitación y transferencia: Sesión presencial de inducción al fundador y a su
colaborador, con manual de usuario que cubre alta de productos, ajuste de
stock,gestión de pedidos y generación de reportes. Se recomienda una segunda
sesión de refuerzo al inicio de la temporada alta.
Respaldos:Respaldo automatizado diario de la base de datos a las 03:00 horas,
con retención de treinta días y copia semanal en almacenamiento externo. Prueba
de restauración trimestral documentada.
Estrategia de temporada baja: Entre noviembre y julio, la instancia se reduce al
plan mínimo del proveedor para disminuir el costo fijo, manteniendo el sitio activo
como vitrina. La capacidad se restablece en agosto, antes del peak.
Monitoreo: Verificación periódica del enrutamiento de WhatsApp, de los enlaces a
redes sociales y del estado del certificado TLS. Revisión mensual de logs de error
y de tiempos de respuesta.
Actualizaciones: Aplicación de parches de seguridad de Django y de
dependencias según el calendario de soporte de la versión LTS, con ventana de
mantenimiento fuera de horario comercial.
Plan de recuperación: Procedimiento documentado de restauración de base de
datos, redeploy de la aplicación y verificación funcional posterior, con
responsables y tiempos objetivos definidos.
Taller de Sistemas de Información • UTEM | Página
37

VOLANTINES STRONG | INFORME FINAL
15. Conclusiones
15.1. Consecuencias de la implementación del proyecto de la empresa
El desarrollo de la plataforma web para Volantines Strong representa una
oportunidad de mejora en la organización y gestión de sus procesos comerciales.
Antes del proyecto, la empresa dependía principalmente de la atención presencial
y de las consultas recibidas mediante Instagram Direct, lo que generaba una alta
carga operativa durante los períodos de mayor demanda, especialmente en
septiembre. La falta de un catálogo digital y de un sistema centralizado para
registrar los pedidos dificulta la consulta de disponibilidad, la coordinación de las
ventas y la preparación anticipada de los productos.
Con la implementación de la solución propuesta, se establece un canal digital que
permite a los clientes consultar el catálogo, revisar las características de los
productos y realizar el proceso de compra anticipada mediante la modalidad Click
& Collect. Asimismo, el panel administrativo facilita la gestión de productos, el
control del stock y el seguimiento de los pedidos, permitiendo organizar las
actividades del taller con mayor anticipación.
De esta manera, el proyecto busca disminuir la dependencia de los canales
informales de atención, reducir las interrupciones de las actividades productivas y
mejorar la experiencia de compra de los clientes. No obstante, el aprovechamiento
de estos beneficios dependerá de la correcta actualización de la información y de
la utilización constante de la plataforma por parte de la empresa.
Taller de Sistemas de Información • UTEM | Página
38

VOLANTINES STRONG | INFORME FINAL
15.2. Problemas enfrentados durante la ejecución del proyecto
Durante el desarrollo del proyecto se presentaron dificultades relacionadas tanto
con la interacción con el cliente como con la organización interna del equipo.
En cuanto a la interacción con el cliente, una de las principales dificultades fue la
preocupación inicial del fundador respecto de la administración de una plataforma
web, principalmente por la posible complejidad de su utilización y los errores que
podrían producirse durante la actualización del inventario. Para abordar esta
situación, se consideró necesario simplificar el panel administrativo, priorizando las
funciones esenciales y facilitando acciones como la modificación del estado de los
pedidos y la gestión de los productos. Además, las demostraciones realizadas con
información real del catálogo permitieron acercar al cliente al funcionamiento de la
solución.
Por otra parte, dentro del equipo de trabajo se presentaron dificultades técnicas
durante las pruebas de carga del sistema. Una de las situaciones más relevantes
fue la saturación del conjunto de conexiones a la base de datos PostgreSQL al
simular la concurrencia de 120 usuarios, lo que provocó errores en las respuestas
del servidor y retrasó las actividades de validación. También se identificaron
dificultades relacionadas con el almacenamiento de archivos multimedia utilizados
en la personalización de carretes, debido a las características del almacenamiento
local del entorno de despliegue.
Estas situaciones requieren coordinación entre los integrantes, revisión de las
responsabilidades técnicas y ajustes en las soluciones implementadas. Como
consecuencia, fue necesario destinar horas adicionales a la resolución de los
problemas y reorganizar algunas actividades, especialmente la entrega de los
reportes analíticos. Sin embargo, estas dificultades permitieron fortalecer la
comunicación interna y mejorar los procedimientos de validación del sistema.
Taller de Sistemas de Información • UTEM | Página
39

VOLANTINES STRONG | INFORME FINAL
15.3. Aprendizajes de la asignatura y su aplicabilidad futura
El desarrollo de este proyecto permitió aplicar de manera práctica los
conocimientos adquiridos en la asignatura Taller de Sistemas de Información,
abordando distintas etapas del ciclo de vida de un proyecto tecnológico. Entre
ellas destacan el levantamiento y análisis de requerimientos, la identificación de
necesidades del cliente, el diseño de la solución, el modelamiento de bases de
datos, la programación, las pruebas y la preparación para la puesta en producción.
Uno de los aprendizajes relevantes fue comprender la importancia del diseño de
bases de datos y de su normalización, particularmente hasta la Tercera Forma
Normal (3FN), ya que permite organizar la información, reducir redundancias y
mantener la integridad de los registros. Asimismo, la utilización del framework
Django y de su arquitectura Modelo-Vista-Template (MVT) permitió comprender
cómo se relacionan los componentes de una aplicación web y cómo se estructura
la interacción entre los usuarios, la lógica del sistema y la información
almacenada.
También fue importante la aplicación de la metodología Scrumban, que facilitó la
distribución de tareas, la visualización del avance y la priorización de actividades
durante el desarrollo. Esta experiencia permitió reconocer que la planificación
debe ser flexible y considerar posibles dificultades técnicas, sin perder de vista los
objetivos y plazos establecidos.
Los conocimientos adquiridos podrán aplicarse en futuros proyectos de desarrollo
de software, especialmente en aquellos que requieran analizar necesidades
reales, diseñar soluciones tecnológicas, administrar información y trabajar
colaborativamente. Además, la experiencia permitió comprender que una solución
informática no debe responder únicamente a criterios técnicos, sino también a las
capacidades, recursos y necesidades de quienes utilizarán el sistema.
Taller de Sistemas de Información • UTEM | Página
40

VOLANTINES STRONG | INFORME FINAL
15.4. Aspectos relevantes del proyecto
Un aspecto importante del proyecto fue la delimitación de su alcance,
particularmente al excluir la gestión de despachos a domicilio y concentrar la
solución en la compra anticipada y el retiro presencial de los productos. Esta
decisión permitió enfocar los esfuerzos en una de las principales dificultades
operativas identificadas en la empresa: la atención de clientes y la preparación de
pedidos durante los períodos de alta demanda.
Asimismo, la incorporación de una herramienta de personalización de carretes
mediante HTML5 Canvas permitió integrar una funcionalidad relacionada
directamente con las necesidades comerciales del negocio, ofreciendo a los
clientes la posibilidad de visualizar sus diseños antes de concretar una compra.
Finalmente, es importante destacar que la continuidad y utilidad de la plataforma
dependerá de su mantenimiento y de la participación activa de la empresa en la
administración del sistema. La actualización del inventario, la gestión de los
pedidos, la realización de respaldos y la capacitación del usuario administrativo
serán fundamentales para conservar su funcionamiento y aprovechar sus
beneficios a largo plazo.
En términos generales, el proyecto permitió desarrollar una solución tecnológica
orientada a una necesidad concreta de una empresa, integrando los
conocimientos técnicos y metodológicos adquiridos durante la asignatura. La
experiencia demostró la importancia de comprender el contexto del cliente,
establecer objetivos claros y mantener una coordinación efectiva entre los
integrantes para desarrollar una propuesta coherente con los problemas
identificados.
Taller de Sistemas de Información • UTEM | Página
41

VOLANTINES STRONG | INFORME FINAL
16. Anexos
16.1. Anexo 1 acta de reuniones
16.1.1. Acta de reunión 1
Tema Solicitar los antecedentes completos respecto al funcionamiento y
operación de la .
Fecha 28/10/2026 Inicio 12:00 Término 12:20
Definición de Roles
Moderador Juan Pablo Vega
Encargado Minuta Pedro Saravia
Participantes Departamento Facultad Firma
Christian Torres Integrante de grupo Facultad de ingeniería Asistió
Pedro Saravia Integrante de grupo Facultad de ingeniería Asistió
Juan Pablo Vega Integrante de grupo Facultad de ingeniería Asistió
Edmundo Moya Integrante de grupo Facultad de ingeniería Asistió
Javiera Flores Líder de grupo Facultad de ingeniería Asistió
Freddy Acosta Dueño de la pyme Pyme Volantines Asistió
Strong
(1) Objetivo de la reunión
1. Se habló sobre la propuesta de trabajo, la historia de la pyme, sus funcionalidades y se
llegó a un acuerdo acorde a las necesidades de la pyme.
2. Registrar acuerdos o dependencias relacionadas con el catálogo, la ficha de productos, el
carrito, el proceso de compra y retiro presencial (Click & Collect), el panel administrativo y
la personalización de carretes.
Taller de Sistemas de Información • UTEM | Página
42

VOLANTINES STRONG | INFORME FINAL
(2) Propósito y Desafíos
Contexto e Hitos
1. Volantines Strong requiere una plataforma web que permita presentar sus productos e
información comercial, facilitar la gestión de pedidos y apoyar la preparación de compras
para retiro presencial.
2. La solución contempla catálogo categorizado, fichas de productos, carrito, registro de
datos del comprador y fecha de retiro, generación de pedido y código de seguimiento,
gestión administrativa de estados y notificación al cliente por WhatsApp.
3. El equipo trabaja con enfoque Scrumban y tablero Kanban con las columnas Backlog, En
Análisis, En Desarrollo, En Revisión y Terminado. Se considera un límite WIP de tres
tareas por subequipo, sincronización dos veces por semana, revisión semanal de avances
y planificación al inicio de cada iteración.
(3) Compromisos
Actividades y compromisos Responsable Fecha sugerida y comprometida
Coordinar una segunda reunión Grupo de 03/11/2026
para validar propuesta y trabajo y cliente
requerimientos iniciales
Elaborar el capítulo 1 hasta el 8 del Grupo de 04/11/2026
primer avance del informe. trabajo
Taller de Sistemas de Información • UTEM | Página
43

VOLANTINES STRONG | INFORME FINAL
16.1.2. Acta de reunión 2
Tema Registrar requerimientos y solicitudes del cliente
Fecha 03/10/2026 Inicio 14:00 Término 14:25
Definición de Roles
Moderador Juan Pablo Vega
Encargado Minuta Pedro Saravia
Participantes Departamento Facultad Firma
Christian Torres Integrante de grupo Facultad de ingeniería Asistió
Pedro Saravia Integrante de grupo Facultad de ingeniería Asistió
Juan Pablo Vega Integrante de grupo Facultad de ingeniería Asistió
Edmundo Moya Integrante de grupo Facultad de ingeniería Asistió
Javiera Flores Líder de grupo Facultad de ingeniería Asistió
Freddy Acosta Dueño de la pyme Pyme Volantines Strong Asistió
(4) Objetivo de la reunión
1. Identificar y recopilar los requerimientos y solicitudes del cliente respecto al desarrollo de
la plataforma web.
2. Conocer las necesidades del negocio y las funcionalidades que espera incorporar en la
solución tecnológica.
3. Definir el alcance inicial del sistema, considerando las prioridades y expectativas del
cliente.
4. Resolver dudas relacionadas con el funcionamiento esperado de la plataforma y sus
distintos módulos.
Taller de Sistemas de Información • UTEM | Página
44

VOLANTINES STRONG  |  INFORME FINAL

(5) Propósito y Desafíos
| Contexto   | e Hitos  |     |     |
| ---------- | -------- | --- | --- |
1.  Se realizó una segunda reunión con el cliente para profundizar en sus necesidades y
expectativas respecto al sistema propuesto.
2.  Se recopilaron los requerimientos funcionales y las solicitudes específicas planteadas por
el cliente.
3.  Se abordó la necesidad de contar con un catálogo digital que permita visualizar los
productos, sus características y disponibilidad.
4.  Se revisó el funcionamiento esperado del proceso de compra, incluyendo el carrito de
compras, la generación de pedidos y el retiro presencial.
5.  Se planteó la incorporación de funcionalidades para facilitar la administración de
productos, el control de stock y la gestión de pedidos.
6.  Se identificaron las necesidades relacionadas con la presentación visual de la plataforma y
la experiencia de navegación del usuario.
7.  La información recopilada servirá como base para la elaboración y priorización del backlog
del producto.

(6) Compromisos
Actividades y compromisos  Responsable  Fecha sugerida y comprometida
| Organizar  | y  documentar  | los  Pedro Saravia  | 03/11/2026  |
| ---------- | -------------- | ------------------- | ----------- |
requerimientos recopilados durante
la reunión.
| Analizar la viabilidad técnica de las  |                      | Equipo               | de  03/11/2026  |
| -------------------------------------- | -------------------- | -------------------- | --------------- |
| funcionalidades solicitadas.           |                      | desarrollo           |                 |
| Priorizar                              | los  requerimientos  | para  Product Owner  | 03/11/2026      |
incorporarlos al Product Backlog.
| Preparar  | una propuesta inicial de  | Equipo         | de  03/11/2026  |
| --------- | ------------------------- | -------------- | --------------- |
| solución  | considerando              | las  trabajo   |                 |
necesidades del cliente.
| Finalizar  | con  el  desarrollo  | del  Equipo  | de  15/11/2026  |
| ---------- | -------------------- | ------------ | --------------- |
| informe    |                      | trabajo      |                 |

Taller de Sistemas de Información • UTEM | Página

45

VOLANTINES STRONG | INFORME FINAL
16.1.3. Acta de reunión 3
Tema Presentación de la propuesta visual de la plataforma y recopilación de
observaciones del cliente
Fecha 10/11/2026 Inicio 14:00 Término 14:25
Definición de Roles
Moderador Juan Pablo Vega
Encargado Minuta Pedro Saravia
Participantes Departamento Facultad Firma
Christian Torres Integrante de grupo Facultad de ingeniería Asistió
Pedro Saravia Integrante de grupo Facultad de ingeniería Asistió
Juan Pablo Vega Integrante de grupo Facultad de ingeniería Asistió
Edmundo Moya Integrante de grupo Facultad de ingeniería Asistió
Javiera Flores Líder de grupo Facultad de ingeniería Asistió
Freddy Acosta Dueño de la pyme Pyme Volantines Strong Asistió
(7) Objetivo de la reunión
1. Presentar al cliente una propuesta inicial del diseño visual de la página web.
2. Revisar la estructura, distribución de contenidos y apariencia general de la plataforma.
3. Recopilar observaciones y sugerencias del cliente respecto al diseño presentado.
4. Consultar sobre el logotipo oficial de la pyme y los elementos gráficos que deben utilizarse
para mantener su identidad visual.
Taller de Sistemas de Información • UTEM | Página
46

VOLANTINES STRONG  |  INFORME FINAL

(8) Propósito y Desafíos
| Contexto   | e Hitos  |     |     |     |
| ---------- | -------- | --- | --- | --- |
1.  Se presentó al cliente una propuesta inicial del diseño de la plataforma web.
2.  Se revisó la distribución de las secciones y la organización visual de los contenidos.
3.  Se consultó al cliente sobre el logotipo de la pyme, con el propósito de definir su
incorporación en la página web.
4.  Se abordó la importancia de mantener una identidad visual coherente con la imagen
comercial de la empresa.
5.  Se recopilaron observaciones para considerar posibles ajustes en el diseño y la
presentación de la plataforma.
6.  Se estableció la necesidad de continuar perfeccionando la propuesta visual antes de
avanzar con su implementación definitiva.

(9) Compromisos
Actividades y compromisos  Responsable  Fecha sugerida y comprometida
| Incorporar  | las  | observaciones  | Edmundo Moya  | 11/11/2026  |
| ----------- | ---- | -------------- | ------------- | ----------- |
realizadas por el cliente al diseño
de la página web.
| Confirmar  | y  recopilar  | el  logotipo  | Juan      | Pablo  10/11/2026  |
| ---------- | ------------- | ------------- | --------- | ------------------ |
| oficial    | de  la  pyme  | para          | su  Vega  |                    |
incorporación en la plataforma.
| Ajustar  | los elementos visuales de  |     | Equipo          | de  11/11/2026  |
| -------- | -------------------------- | --- | --------------- | --------------- |
| acuerdo  | con  la  identidad         | de  | la  desarrollo  |                 |
empresa.
| Presentar                      | una versión actualizada  |     | Equipo      | de  14/11/2026  |
| ------------------------------ | ------------------------ | --- | ----------- | --------------- |
| del diseño para su revisión.   |                          |     | desarrollo  |                 |
| Revisión final del informe     |                          |     | Equipo      | de  16/11/2026  |
desarrollo

Taller de Sistemas de Información • UTEM | Página

47

VOLANTINES STRONG | INFORME FINAL
16.2. Diagramas complementarios
16.2.1. Diagrama de Flujo de Datos Actual
Figura 2. Diagrama de flujo de datos actual.
16.2.2. Diagrama de Flujo de Datos Propuesto
Figura 3. Diagrama de flujo de datos propuesto.
Taller de Sistemas de Información • UTEM | Página
48

VOLANTINES STRONG | INFORME FINAL
16.2.3. Diagrama de Flujo del Proceso de Venta y Retiro
Figura 4. Diagrama de flujo de procesos.
16.3. Enlaces del proyecto
● Tablero Kanban:
https://trello.com/invite/b/6afd02650ef17722d07dad36/ATTI64992a3f20ac9d40e54
93edc7037ce68CE556B46/volanties-strong
Taller de Sistemas de Información • UTEM | Página
49