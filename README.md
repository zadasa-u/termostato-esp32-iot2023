# termostato-esp32-iot2023

Crear un termostato con un esp32 que puede funcionar de modo manual o automático y que cumpla con las siguientes especificaciones:

- Programado en micropython utilizando asyncio
- sensor dht22.
- se comunica mediante mqtts.
- publica periódicamente en el tópico "ID del dispositivo" los siguientes parámetros: temperatura, humedad, setpoint, periodo y modo.
- se envía en una sola publicación en un JSON
- se suscriba a setpoint, periodo, destello, modo y relé.
- almacenará de manera no volátil los parámetros de setpoint, periodo, modo y relé (ver btree).
- contará con relé que se accionará cuando se supere la temperatura de setpoint. (modo automático)
- si se encuentra en modo manual el relé se activará según la orden "relé" enviada por mqtt.
- destellará por unos segundos cuando reciba la orden "destello" por mqtt.
- cuando recibe un mensaje con nuevos parámetros deberá actualizar los almacenados y actuar si es necesario.
- el código del programa deberá estar en un repositorio git cuya dirección debe figurar en la entrega del trabajo.
