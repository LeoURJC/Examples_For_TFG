# Examples_For_TFG
In this repository I'll practice with github. Until I create the repository of my TFG. 

## Índice 

1. Ejercicio 1: Figuras


## Ejercicio 1: Figuras

La finalidad de este ejercicio es hacer que el robot haga una figura geomérica en este caso un **cuadrado** y un **triangulo**

Para ello se ha realizado un sistema de comunicación entre nodos de *cliente - servidor* donde nosotros seremos capaces de enviarle al robot la figura que este ha de trazar. 
Por otra parte para el cálculo de los giros (90º en caso de querer hacer un cuadrado y 120º en caso de querer hacer un triángulo) se ha usado el tópico de **/odom** 

A demás que para desplazamientos de errores y reseterar el robot a su posición inicial se le puede pedir al robot que recupere su posicion inicial respecto a su eje Z 
(lo que sería la güiñada o yaw) escribiendo por el terminal "Reiniciar". 

A demás de que en caso de parada de emergencia se ha establecido un comando de "Stop" donde si es tecleado por el terminal el robot parara en seco. 


