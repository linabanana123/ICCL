# Import necessary libraries 
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app import app
from functions import process_discovery, conformance_checking
import dash_interactive_graphviz
import base64
import dash
import pickle, codecs

# conformance measure dropdown
conformance_dropdown = dcc.Dropdown(id='conformance-measure', options=['Fitness', 'Precision'], multi=False, value='Fitness')

# Define the page layout
layout = dbc.Container([
    dbc.Col([
        html.Center(html.H1("Process Discovery Original OCEL")),
        html.Hr(),
        dbc.Row([
            dbc.Col([html.Div("Select Conformance Measure:")], align='center'),
            dbc.Col([conformance_dropdown], align='center'),
            dbc.Col([dbc.Button("Calculate", id="calc-conformance", className="me-2", n_clicks=0)], align='center'),
            dbc.Col([html.Div("Result:")], align='center'),
            dbc.Col([html.Div(id='conformance-result')], align='center'),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Button("Show Process Model", color="warning", className="me-1", id='start-pm', n_clicks=0),
        ]),
        html.Div(id='pm-model'),
        html.Div(id='pm-model-display')
    ])
])

@app.callback(Output("conformance-result", "children"), [State("ocel_obj", "data"), State("conformance-measure", "value")], [Input("calc-conformance", "n_clicks")])
def on_button_click(ocel_obj, conformance_meas, n):
    if n > 0:
        # load ocel
        ocel_log = pickle.loads(codecs.decode(ocel_obj.encode(), "base64"))
        # discover petri net
        ocpn = process_discovery.process_discovery_ocel_to_ocpn(ocel_log)
        # calculate fitness or precision, return as html div
        if conformance_meas == 'Fitness':
            fitness = conformance_checking.calculate_fitness(ocel_log, ocpn)
            result = html.Div(str(fitness))
        elif conformance_meas == 'Precision':
            precision = conformance_checking.calculate_precision(ocel_log, ocpn)
            result = html.Div(str(precision))
        return result
    else:
        return dash.no_update


@app.callback([Output("pm-model", "children"), Output("pm-model-display", "children")], State("ocel_obj", "data"), [Input("start-pm", "n_clicks")])
def on_button_click(ocel_obj, n):
    if n > 0:
        # load ocel
        ocel_log = pickle.loads(codecs.decode(ocel_obj.encode(), "base64"))
        # discover petri net
        #process_discovery.process_discovery_ocel_to_img(ocel_log, "oc_petri_net")
        ocpn = process_discovery.process_discovery_ocel_to_ocpn(ocel_log)
        # convert ocpn to gviz str
        gviz_ocpn = process_discovery.ocpn_to_gviz(ocpn)
        # create interactive dash gviz object
        ocpn_vis = dash_interactive_graphviz.DashInteractiveGraphviz(id="ocpn-original-ocel",dot_source=str(gviz_ocpn))
        return "Process Model successfully discovered.", ocpn_vis
    else:
        return dash.no_update

