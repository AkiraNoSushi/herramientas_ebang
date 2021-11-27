# Herramientas para miners

Este repositorio aloja múltiples herramientas que utilicé para mantenimiento de granjas de criptomonedas

## Instalación

Estos scripts fueron escritos inicialmente en Python 3.10, así que es preferible mantenerse en versiones igual o superiores. Sin embargo, actualmente son compatibles con versiones anteriores, sólo hasta Python 3.6

Requieren de la librería `requests`, la cual se puede instalar utilizando `pip`:

```bash
pip install requests
```

## Uso

### diagnostico_ebit.py:
```bash
python diagnostico_ebit.py <inicio del rango de IPs> <fin del rango de IPs>
``` 

La herramienta, por defecto, va a mostrar en pantalla las máquinas que estén rindiendo un 40% menos de 9TH/s, con su hashrate actual, sus temperaturas por hashboards y la velocidad de los ventiladores. Estos valores son configurables dentro del script.

### reemplazar_pool_ebit.py:
```bash
python reemplazar_pool_ebit.py <inicio del rango de IPs> <fin del rango de IPs> <dirección de la pool a configurar> <3 puertos separados por ,> <prefijo del nombre de usuario>
``` 
Después del prefijo escogido, el script colocará automáticamente el último número de la dirección IP de cada miner, para fácil identificación al conectarse a la pool. Hay que tener en cuenta que esto podría causar conflictos en caso de especificar un rango de IPs que abarque 2 capas.
