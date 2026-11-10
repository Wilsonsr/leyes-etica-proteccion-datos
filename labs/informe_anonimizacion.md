# Informe de riesgo de reidentificación · DataMarket → proveedor

**Equipo:** Docente · versión de referencia  ·  **Fecha:** 2026-11-10

## 1. Qué se entrega
- Versión: **V2 · generalización fuerte + supresión** · salida elegida: **1 · base anonimizada con utilidad reducida**
- 1,226 registros de 1,512 · 14 variables: id_seudo, edad, sexo, ciudad, ocupacion, estrato, visitas_web, productos_vistos, compras_6m, monto_compras, recencia_dias, canal_adquisicion, categoria_top, churn

## 2. Qué se midió (escenario: el atacante conoce edad, sexo, ciudad y ocupación)
| Métrica | Línea base (V0) | Entregable |
|:--|--:|--:|
| % registros con k<5 | 100.0 | 0.0 |
| Prob. media de reidentificación % | 91.6 | 8.9 |
| % reidentificado en el ataque | 82.7 | 0.0 |
| AUC del modelo de abandono | 0.823 | 0.825 |

## 3. Umbral aceptado y por qué
k ≥ 5 para el 100 % de los registros y <5 % de la fuente pública reidentificada. El abandono depende del comportamiento, no de la demografía fina: V2 conserva casi todo el AUC y reduce el ataque de vinculación a casi cero.

## 4. Riesgo residual
Vale para el escenario declarado. No cubre atacantes con información adicional
(compras exactas, fechas) ni el cruce con otras bases del proveedor.

## 5. Condiciones de la entrega
Acuerdo de transmisión con prohibición de cruce y de reidentificación; uso exclusivo para el motor de recomendación; destrucción a los 6 meses; auditoría.
