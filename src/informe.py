"""Arma el informe HTML autocontenido: las graficas van embebidas en base64."""
import base64
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = Path("/tmp/claude-1000/-home-angelvargas/cd6aef75-90b3-4b67-a92b-681259bf9ad8/scratchpad/informe_xm.html")
h = json.loads((RAIZ / "hallazgos.json").read_text())


def img(nombre: str) -> str:
    b64 = base64.b64encode((RAIZ / "graficas" / nombre).read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def figura(nombre: str, pie: str) -> str:
    return (f'<figure><img src="{img(nombre)}" alt="{pie}">'
            f'<figcaption>{pie}</figcaption></figure>')


CSS = """
:root{
  --tinta:#161d26; --tinta-2:#3d4b5c; --suave:#6d7f92;
  --fondo:#f7f8fa; --papel:#ffffff; --linea:#dfe5ec;
  --acento:#1c4f8b; --acento-suave:#e8eff7;
  --alerta:#a8541f; --alerta-suave:#f8eee4; --ok:#2c7259;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --tinta:#e8edf3; --tinta-2:#b6c2d0; --suave:#8a99a9;
    --fondo:#10151b; --papel:#161d26; --linea:#28323e;
    --acento:#7db0e8; --acento-suave:#1a2839;
    --alerta:#e0a06a; --alerta-suave:#2c2118; --ok:#6ec2a0;
  }
}
:root[data-theme="dark"]{
  --tinta:#e8edf3; --tinta-2:#b6c2d0; --suave:#8a99a9;
  --fondo:#10151b; --papel:#161d26; --linea:#28323e;
  --acento:#7db0e8; --acento-suave:#1a2839;
  --alerta:#e0a06a; --alerta-suave:#2c2118; --ok:#6ec2a0;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--fondo); color:var(--tinta);
  font-family:"Source Serif 4",Georgia,serif; font-size:18px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.envoltura{max-width:1120px; margin:0 auto; padding:0 24px 96px}
.columna{max-width:660px}
h1,h2,h3,.dato,.eyebrow,figcaption,th,.pie{font-family:Archivo,"Helvetica Neue",Arial,sans-serif}

header.portada{border-bottom:2px solid var(--tinta); padding:56px 0 26px; margin-bottom:44px}
.eyebrow{font-size:12px; letter-spacing:.16em; text-transform:uppercase; color:var(--acento); font-weight:600}
h1{font-size:clamp(34px,5.4vw,56px); line-height:1.04; margin:14px 0 16px; font-weight:800;
   letter-spacing:-.022em; text-wrap:balance; max-width:16ch}
.bajada{font-size:20px; color:var(--tinta-2); max-width:60ch; margin:0 0 28px}
.credencial{display:flex; flex-wrap:wrap; gap:8px 30px; font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:12.5px; color:var(--suave); border-top:1px solid var(--linea); padding-top:16px}
.credencial b{color:var(--tinta-2); font-weight:500}

.tablero{display:grid; grid-template-columns:repeat(auto-fit,minmax(178px,1fr)); gap:1px;
  background:var(--linea); border:1px solid var(--linea); margin:0 0 56px}
.celda{background:var(--papel); padding:20px 18px}
.celda .rotulo{font-family:Archivo,sans-serif; font-size:11px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--suave); margin-bottom:10px}
.celda .dato{font-size:31px; font-weight:800; letter-spacing:-.02em; font-variant-numeric:tabular-nums; line-height:1}
.celda .nota{font-size:13.5px; color:var(--tinta-2); margin-top:8px; line-height:1.42}
.sube .dato{color:var(--alerta)}
.marca .dato{color:var(--acento)}

section{margin-bottom:64px}
h2{font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--suave);
   font-weight:600; margin:0 0 10px; display:flex; align-items:baseline; gap:12px}
h2 .num{font-family:"IBM Plex Mono",monospace; color:var(--acento); font-size:12px}
h3{font-size:clamp(23px,3vw,31px); line-height:1.18; margin:0 0 18px; font-weight:700;
   letter-spacing:-.015em; text-wrap:balance; max-width:22ch}
p{margin:0 0 18px}
strong{font-weight:700; color:var(--tinta)}
.cifra{font-family:"IBM Plex Mono",monospace; font-size:.93em; font-variant-numeric:tabular-nums;
  background:var(--acento-suave); color:var(--acento); padding:1px 5px; border-radius:2px; font-weight:500}

figure{margin:30px 0 0; background:var(--papel); border:1px solid var(--linea); padding:14px}
figure img{width:100%; height:auto; display:block}
figcaption{font-size:12.5px; color:var(--suave); margin-top:12px; padding-top:10px;
  border-top:1px solid var(--linea); line-height:1.45}

.aviso{border-left:3px solid var(--alerta); background:var(--alerta-suave); padding:16px 20px;
  font-size:15.5px; color:var(--tinta-2); margin:26px 0 0}
.aviso p{margin:0}
.aviso p + p{margin-top:12px}

.metodo{background:var(--papel); border:1px solid var(--linea); padding:34px 34px 14px; margin-top:12px}
.metodo h3{font-size:22px; max-width:none}
.metodo .columna{max-width:none}
table{width:100%; border-collapse:collapse; font-size:14.5px; margin:6px 0 24px}
th,td{text-align:left; padding:9px 12px 9px 0; border-bottom:1px solid var(--linea); vertical-align:top}
th{font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--suave); font-weight:600}
td code{font-family:"IBM Plex Mono",monospace; font-size:13px; color:var(--acento)}
.desliza{overflow-x:auto}

footer{border-top:2px solid var(--tinta); padding-top:26px; margin-top:8px}
footer .columna{max-width:70ch}
footer p{font-size:15.5px; color:var(--tinta-2)}
.pie{font-size:12px; color:var(--suave); font-family:"IBM Plex Mono",monospace; margin-top:22px; line-height:1.7}
a{color:var(--acento)}
a:focus-visible,:focus-visible{outline:2px solid var(--acento); outline-offset:3px}
@media (max-width:640px){ body{font-size:17px} .envoltura{padding:0 18px 64px} }
"""


HTML = f"""<title>Mercado eléctrico 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap">
<style>{CSS}</style>

<div class="envoltura">
<header class="portada">
  <div class="eyebrow">Análisis con datos públicos de XM</div>
  <h1>La energía se encareció 8 veces y el agua no tuvo la culpa</h1>
  <p class="bajada">Doce meses del mercado eléctrico colombiano: qué pasó con el precio de bolsa,
     por qué la explicación hidrológica no alcanza, y qué significa para un comercializador
     tener parte de su demanda sin contratos.</p>
  <div class="credencial">
    <span><b>Ángel Farid Agreda Vargas</b> · Ing. de Sistemas, Universidad Libre Cali</span>
    <span>Ventana: <b>{h['ventana_inicio']} a {h['ventana_fin']}</b></span>
    <span>Fuente: <b>servapibi.xm.com.co</b></span>
  </div>
</header>

<div class="tablero">
  <div class="celda sube">
    <div class="rotulo">Precio de bolsa hoy</div>
    <div class="dato">982</div>
    <div class="nota">COP/kWh en agosto 2026. En febrero eran 124.</div>
  </div>
  <div class="celda">
    <div class="rotulo">Contratos regulados</div>
    <div class="dato">334</div>
    <div class="nota">COP/kWh. La bolsa cuesta 2,9 veces más.</div>
  </div>
  <div class="celda">
    <div class="rotulo">Embalses</div>
    <div class="dato">78,5<span style="font-size:19px">%</span></div>
    <div class="nota">Volumen útil, por encima del promedio del año.</div>
  </div>
  <div class="celda marca">
    <div class="rotulo">Vatia en el país</div>
    <div class="dato">N.º 11</div>
    <div class="nota">De 65 comercializadores. 2,07% de la demanda nacional.</div>
  </div>
</div>

<section>
  <div class="columna">
    <h2><span class="num">01</span> El precio</h2>
    <h3>La bolsa se despegó de los contratos</h3>
    <p>El precio de bolsa promedió <span class="cifra">361,8 COP/kWh</span> en los doce meses,
       pero el promedio esconde el movimiento: pasó de <strong>124 COP/kWh en febrero de 2026</strong>
       a <strong>982 COP/kWh en agosto</strong>, casi ocho veces, con un máximo diario de
       <span class="cifra">1.033 COP/kWh</span> el 5 de agosto de 2026.</p>
    <p>Los contratos no se movieron: el precio promedio en el mercado regulado sigue cerca de
       <strong>334 COP/kWh</strong>. Es la brecha que define el negocio ahora mismo — cada kWh que
       hoy se compra en bolsa cuesta <strong>2,9 veces</strong> lo que cuesta bajo contrato.</p>
  </div>
  {figura("01_precio_bolsa.png", "Precio de bolsa nacional (promedio diario) contra el precio promedio de contratos, agosto 2025 – agosto 2026.")}
</section>

<section>
  <div class="columna">
    <h2><span class="num">02</span> La causa</h2>
    <h3>Los embalses están normales</h3>
    <p>La explicación intuitiva es la sequía, y los datos no la sostienen. Los embalses cerraron
       la ventana en <strong>78,5% de volumen útil</strong>, por encima del promedio del año
       (<strong>76,3%</strong>), y la correlación entre precio y nivel de embalses es
       prácticamente nula: <span class="cifra">−0,07</span>.</p>
    <p>Donde sí hay señal es en los aportes: la correlación con el caudal que entra a los embalses
       es <span class="cifra">−0,48</span>, y en agosto los aportes están en <strong>68,7% de su
       media histórica</strong>. Hay agua guardada, pero está entrando menos de la que debería, y
       el precio responde a ese flujo — y a lo que cuesta la generación térmica que lo reemplaza —
       más que al nivel del embalse.</p>
  </div>
  {figura("02_hidrologia.png", "Precio de bolsa contra volumen útil de los embalses y aportes hídricos como porcentaje de la media histórica.")}
</section>

<section>
  <div class="columna">
    <h2><span class="num">03</span> El día</h2>
    <h3>Ya casi no quedan horas baratas</h3>
    <p>En mayo de 2026 el día todavía tenía forma: valle en la madrugada, pico a las 20:00, y el
       pico costaba <strong>2,2 veces</strong> el valle. En agosto la curva se aplanó hacia arriba.
       La hora más barata está en <strong>853 COP/kWh</strong> y la más cara solo la supera en
       <span class="cifra">23%</span>.</p>
    <p>Eso cambia el argumento comercial. A un cliente no regulado se le podía ofrecer ahorro
       moviendo consumo fuera del pico; con la curva aplanada ese margen se encogió y el valor
       vuelve a estar en la cobertura contractual, no en el horario.</p>
  </div>
  {figura("03_perfil_horario.png", "Precio promedio por hora del día en tres meses distintos: febrero, mayo y agosto de 2026.")}
</section>

<section>
  <div class="columna">
    <h2><span class="num">04</span> El mercado</h2>
    <h3>Dónde está Vatia entre 65 comercializadores</h3>
    <p>Vatia atendió <strong>1.777,5 GWh</strong> en los últimos doce meses, el
       <strong>2,07%</strong> de la demanda nacional: el <strong>puesto 11</strong> entre los
       65 comercializadores activos, en un mercado donde los cuatro primeros concentran más de la
       mitad. Su demanda es <strong>90% regulada</strong> (1.599,2 GWh) y 10% no regulada
       (178,3 GWh).</p>
  </div>
  {figura("05_ranking.png", "Demanda comercial atendida en doce meses por los quince comercializadores más grandes del país.")}
</section>

<section>
  <div class="columna">
    <h2><span class="num">05</span> El riesgo</h2>
    <h3>La exposición a bolsa dejó de ser un ahorro</h3>
    <p>Cruzando la demanda de cada comercializador con la energía que tiene respaldada en contratos
       se ve qué porción termina comprando en bolsa. Vatia compró allí el <strong>13,1% de su
       demanda</strong> en promedio durante el año, y <strong>20,5% en agosto de 2026</strong>,
       frente a una mediana del mercado de <strong>7,5%</strong> y <strong>9,2%</strong>.</p>
  </div>
  {figura("04_exposicion.png", "Porcentaje de la demanda comprada en bolsa, mes a mes: Vatia contra la mediana de los comercializadores del país.")}
  <div class="columna">
    <p style="margin-top:34px">Estar expuesto no era un error: mientras la bolsa estuvo por debajo
       de los contratos, comprar allí <strong>ahorraba</strong> dinero, y eso es lo que muestran las
       barras verdes hasta abril. En mayo el signo se invirtió. Valorando la energía expuesta contra
       el precio de contratos regulados, el diferencial llega a
       <strong>+15,4 mil millones de COP en julio</strong> y <strong>+10,5 mil millones en lo
       corrido de agosto</strong>.</p>
  </div>
  {figura("06_costo_exposicion.png", "Energía expuesta de Vatia multiplicada por la diferencia entre el precio de bolsa y el de contratos regulados, por mes.")}
  <div class="columna">
    <div class="aviso">
      <p><strong>Qué no es esta cifra.</strong> Es una estimación de orden de magnitud, no la
         posición financiera de la empresa. Usa el precio promedio de contratos del sistema, no el
         de los contratos de cada agente, que no es público. No incluye contratos de respaldo,
         coberturas financieras ni cargo por confiabilidad. Sirve para dimensionar por qué la
         cobertura importa hoy, no para auditar a nadie.</p>
    </div>
  </div>
</section>

<section class="metodo">
  <div class="columna">
    <h2><span class="num">◆</span> Método</h2>
    <h3>Dos cosas que aparecieron al trabajar los datos</h3>
    <p><strong>Las etiquetas de contratos cambian de orientación según el mes.</strong> En las
       series por agente, <code>CompContEner</code> y <code>VentContEner</code> son los dos lados
       del mismo contrato y a nivel sistema suman exactamente igual —verificado: 10.237,7 GWh
       contra 10.237,7 GWh en julio de 2026—. Pero cuál de las dos trae la energía que respalda la
       demanda de un comercializador cambia: hasta junio de 2026 venía en <code>CompContEner</code>;
       en julio y agosto de 2026, y también en diciembre de 2025, viene en
       <code>VentContEner</code>. Tomar la etiqueta literalmente produce resultados imposibles,
       como que Enel comprara en bolsa el 196% de su demanda. La regla que quedó en el código es no
       confiar en la etiqueta: para cada agente y mes, el mayor de los dos valores es la energía que
       respalda su demanda y el menor son sus ventas a terceros. Con eso, las exposiciones de los 65
       comercializadores caen en el rango razonable de 0% a 35%.</p>
    <p><strong>Diciembre de 2025 quedó fuera.</strong> Ese mes la energía en contratos reportada
       cae para todos los agentes a la vez y dispara la exposición aparente del mercado entero a
       valores de 50% a 97%. Es un problema de la fuente, no del cálculo, así que se excluye de las
       gráficas de exposición y de costo, y así está anotado en ellas.</p>
    <h3 style="margin-top:34px">Cómo está hecho</h3>
    <p>Python con pandas y matplotlib. La API de XM entrega máximo 31 días por petición, así que el
       cliente parte el rango en tramos, reintenta ante fallos y cachea cada respuesta en disco.
       Ninguna cifra de este informe está escrita a mano: todas salen de
       <code>hallazgos.json</code>, que genera el mismo código que dibuja las gráficas.</p>
    <div class="desliza">
    <table>
      <tr><th>Serie</th><th>Métrica de XM</th><th>Para qué</th></tr>
      <tr><td>Precio de bolsa</td><td><code>PrecBolsNaci</code></td><td>Precio horario del mercado</td></tr>
      <tr><td>Precio de contratos</td><td><code>PrecPromContRegu</code>, <code>PrecPromContNoRegu</code></td><td>Referencia de cobertura</td></tr>
      <tr><td>Demanda comercial</td><td><code>DemaCome</code>, <code>DemaComeReg</code>, <code>DemaComeNoReg</code></td><td>Tamaño y mezcla de cada agente</td></tr>
      <tr><td>Contratos</td><td><code>CompContEner</code>, <code>VentContEner</code></td><td>Energía respaldada</td></tr>
      <tr><td>Hidrología</td><td><code>PorcVoluUtilDiar</code>, <code>PorcApor</code></td><td>Embalses y aportes</td></tr>
      <tr><td>Agentes</td><td><code>ListadoAgentes</code></td><td>Códigos y actividad</td></tr>
    </table>
    </div>
  </div>
</section>

<footer>
  <div class="columna">
    <p>Soy estudiante de octavo semestre de Ingeniería de Sistemas en la Universidad Libre
       Seccional Cali y estoy buscando dónde hacer mi práctica. Hice este análisis para entender
       el negocio de una comercializadora de energía antes de tocar la puerta. No tengo experiencia
       profesional en el sector: todo lo de acá salió de la documentación de XM y de trabajar los
       datos.</p>
    <p class="pie">
      Ángel Farid Agreda Vargas · simmonsvampire@gmail.com · github.com/angelfvargas<br>
      Código y datos: github.com/angelfvargas/mercado-energia-xm<br><br>
      Análisis independiente, hecho con información pública. No está afiliado, patrocinado ni
      avalado por XM ni por ninguna de las empresas mencionadas. Datos descargados el 20 de agosto
      de 2026; la liquidación del mercado tiene días de rezago, por eso la ventana termina el 17.
    </p>
  </div>
</footer>
</div>
"""

SALIDA.write_text(HTML, encoding="utf-8")
print(SALIDA, f"{SALIDA.stat().st_size/1024:.0f} KB")
