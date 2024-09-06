from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import clips  # Asegúrate de que CLIPS está instalado y configurado

app = Flask(__name__)

# Integración con CLIPS
sistemaExperto = clips.Environment()
sistemaExperto.clear()

# Definir las reglas en CLIPS
reglaNormal = "(defrule Normal ?f <- (numero ?num) (test (<= ?num 3)) => (assert (diagnostico Normal)))"
reglaResfriado = "(defrule Resfriado ?f <- (numero ?num) (test (<= ?num 8)) => (assert (diagnostico Resfriado)))"
reglaGripe = "(defrule Gripe ?f <- (numero ?num) (test (>= ?num 8)) => (assert (diagnostico Gripe)))"
reglaRecomendaciones = "(defrule Recomendaciones (or (diagnostico Resfriado) (diagnostico Gripe)) => (assert (recomendacion Consulta con un médico y descansa adecuadamente.)))"

# Definición de variables
Comienzo_de_sintomas = ctrl.Antecedent(
    np.arange(0, 10, 0.5), 'Comienzo_de_sintomas')
Fiebre = ctrl.Antecedent(np.arange(0, 10, 0.5), 'Fiebre')
Dolores = ctrl.Antecedent(np.arange(0, 10, 0.5), 'Dolores')
Fatiga_debilidad = ctrl.Antecedent(np.arange(0, 10, 0.5), 'Fatiga_debilidad')
Dolor_de_cabeza = ctrl.Antecedent(np.arange(0, 10, 0.5), 'Dolor_de_cabeza')
Congestión_estornudos_o_dolor_de_garganta = ctrl.Antecedent(
    np.arange(0, 10, 0.5), 'Congestión_estornudos_o_dolor_de_garganta')
Diagnostico = ctrl.Consequent(np.arange(0, 10, 0.5), 'Diagnostico')

# Configurar Membership Function


def configure_membership_functions():
    Comienzo_de_sintomas['Normal'] = fuzz.trapmf(
        Comienzo_de_sintomas.universe, [0, 0, 1.5, 3])
    Comienzo_de_sintomas['Gradual'] = fuzz.trapmf(
        Comienzo_de_sintomas.universe, [2.5, 4, 7, 7.5])
    Comienzo_de_sintomas['Repentino'] = fuzz.trapmf(
        Comienzo_de_sintomas.universe, [7, 9, 10, 10])

    Fiebre['Normal'] = fuzz.trapmf(Fiebre.universe, [0, 0, 1.5, 3])
    Fiebre['Aveces'] = fuzz.trapmf(Fiebre.universe, [2.5, 4, 7, 7.5])
    Fiebre['Amenudo'] = fuzz.trapmf(Fiebre.universe, [7, 9, 10, 10])

    Dolores['Normal'] = fuzz.trapmf(Dolores.universe, [0, 0, 1.5, 3])
    Dolores['Aveces'] = fuzz.trapmf(Dolores.universe, [2.5, 4, 7, 7.5])
    Dolores['Amenudo'] = fuzz.trapmf(Dolores.universe, [7, 9, 10, 10])

    Fatiga_debilidad['Normal'] = fuzz.trapmf(
        Fatiga_debilidad.universe, [0, 0, 1.5, 3])
    Fatiga_debilidad['Aveces'] = fuzz.trapmf(
        Fatiga_debilidad.universe, [2.5, 4, 7, 7.5])
    Fatiga_debilidad['Amenudo'] = fuzz.trapmf(
        Fatiga_debilidad.universe, [7, 9, 10, 10])

    Dolor_de_cabeza['Normal'] = fuzz.trapmf(
        Dolor_de_cabeza.universe, [0, 0, 1.5, 3])
    Dolor_de_cabeza['Aveces'] = fuzz.trapmf(
        Dolor_de_cabeza.universe, [2.5, 4, 7, 7.5])
    Dolor_de_cabeza['Amenudo'] = fuzz.trapmf(
        Dolor_de_cabeza.universe, [7, 9, 10, 10])

    Congestión_estornudos_o_dolor_de_garganta['Normal'] = fuzz.trapmf(
        Congestión_estornudos_o_dolor_de_garganta.universe, [0, 0, 1.5, 3])
    Congestión_estornudos_o_dolor_de_garganta['Aveces'] = fuzz.trapmf(
        Congestión_estornudos_o_dolor_de_garganta.universe, [2.5, 4, 7, 7.5])
    Congestión_estornudos_o_dolor_de_garganta['Amenudo'] = fuzz.trapmf(
        Congestión_estornudos_o_dolor_de_garganta.universe, [7, 9, 10, 10])

    Diagnostico['Normal'] = fuzz.trimf(Diagnostico.universe, [0, 0, 3])
    Diagnostico['Resfriado'] = fuzz.trimf(Diagnostico.universe, [2, 5, 8])
    Diagnostico['Gripe'] = fuzz.trimf(Diagnostico.universe, [7, 10, 10])

    # Reglas
    rule1 = ctrl.Rule(Comienzo_de_sintomas['Normal'] & Fiebre['Normal'] & Dolores['Normal'] &
                      Fatiga_debilidad['Normal'] & Dolor_de_cabeza['Normal'] &
                      Congestión_estornudos_o_dolor_de_garganta['Normal'], Diagnostico['Normal'])

    rule2 = ctrl.Rule(Comienzo_de_sintomas['Gradual'] & Fiebre['Aveces'] & Dolores['Aveces'] &
                      Fatiga_debilidad['Aveces'] & Dolor_de_cabeza['Aveces'] &
                      Congestión_estornudos_o_dolor_de_garganta['Aveces'], Diagnostico['Resfriado'])

    rule3 = ctrl.Rule(Comienzo_de_sintomas['Repentino'] & Fiebre['Amenudo'] & Dolores['Amenudo'] &
                      Fatiga_debilidad['Amenudo'] & Dolor_de_cabeza['Amenudo'] &
                      Congestión_estornudos_o_dolor_de_garganta['Amenudo'], Diagnostico['Gripe'])

    Diagnostico_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    return ctrl.ControlSystemSimulation(Diagnostico_ctrl)

# Página de inicio que muestra el formulario


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recibir datos del formulario
        try:
            comienzo_de_sintomas = float(request.form['comienzo'])
            fiebre = float(request.form['fiebre'])
            dolores = float(request.form['dolores'])
            fatiga_debilidad = float(request.form['fatiga'])
            dolor_de_cabeza = float(request.form['dolor_cabeza'])
            congestion_estornudos_o_dolor_de_garganta = float(
                request.form['congestion'])
        except ValueError:
            return render_template('index.html', greeting='Error: Todos los campos deben ser números.')

        # Inicializar el sistema de control
        prop = configure_membership_functions()

        # Asignar los valores al sistema de control
        prop.input['Comienzo_de_sintomas'] = comienzo_de_sintomas
        prop.input['Fiebre'] = fiebre
        prop.input['Dolores'] = dolores
        prop.input['Fatiga_debilidad'] = fatiga_debilidad
        prop.input['Dolor_de_cabeza'] = dolor_de_cabeza
        prop.input['Congestión_estornudos_o_dolor_de_garganta'] = congestion_estornudos_o_dolor_de_garganta

        # Calcular el resultado
        prop.compute()

        # Obtener el valor de Diagnóstico
        diagnostico = prop.output['Diagnostico']

        # Construir reglas en CLIPS
        sistemaExperto.reset()  # Asegúrate de que el entorno esté limpio antes de agregar reglas
        sistemaExperto.build(reglaNormal)
        sistemaExperto.build(reglaResfriado)
        sistemaExperto.build(reglaGripe)
        sistemaExperto.build(reglaRecomendaciones)

        # Afirmar el diagnóstico en CLIPS
        sistemaExperto.assert_string(f"(numero {diagnostico})")
        sistemaExperto.run()

        # Obtener el resultado de CLIPS
        resultado_diagnostico = "No determinado"
        recomendacion = "No hay recomendaciones disponibles"

        for fact in sistemaExperto.facts():
            fact_str = str(fact)  # Convertir el hecho a cadena
            if 'diagnostico' in fact_str:
                resultado_diagnostico = fact_str.split()[1]
            if 'recomendacion' in fact_str:
                recomendacion = ' '.join(fact_str.split()[1:])

        return render_template('index.html', greeting=f'Diagnóstico: {resultado_diagnostico}. Recomendación: {recomendacion}')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
