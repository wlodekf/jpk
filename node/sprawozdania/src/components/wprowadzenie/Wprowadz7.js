import React, { Component } from 'react';
import { Tekst } from '../forms';
import { formatText, skrotTekstu } from '../../utils/utils';

// Polityka arachunkowości

function TekstSkrot(props) {
    return (
        <a href="/" className="list-group-item" onClick={props.fullText(props.nazwa)}>
            <h4 className="list-group-item-heading nag">{props.etykieta}</h4>
            {skrotTekstu(props.form[props.nazwa])}
        </a>
    );
}

class Wprowadz7 extends Component {

    render() {
        return (
            <div className="list-group">
                <TekstSkrot nazwa="p7_zasady" {...this.props} etykieta="Omówienie przyjętych zasad (polityki) rachunkowości, w zakresie w jakim ustawa pozostawia jednostce prawo wyboru"/>
                <div className="wtracenie">
                    w tym:
                </div>
                <TekstSkrot nazwa="p7_wycena" {...this.props} etykieta="metod wyceny aktywów i pasywów (także amortyzacji)"/>
                <TekstSkrot nazwa="p7_wynik" {...this.props} etykieta="ustalenia wyniku finansowego"/>
                <TekstSkrot nazwa="p7_spraw" {...this.props} etykieta="ustalenia sposobu sporządzenia sprawozdania finansowego"/>
            </div>
        );
    }
}

export function FullText(props) {
    return (
        <div>
            <h4 className="list-group-item-heading nag">{props.etykieta}</h4>

            {formatText(props.form[props.pole])}

            <button className="btn btn-default" onClick={props.onFullTextEdit}>Zmień</button>
            <button className="btn btn-default" onClick={props.onFullTextBack}>Powrót do wprowadzenia</button>
        </div>
    );
}

export function FullTextEdit(props) {
    return (
        <div>
            <h4 className="list-group-item-heading nag">{props.etykieta}</h4>

            <Tekst nazwa={props.pole} rows="10" value={props.form[props.pole]} {...props} onMount={props.onMount}/>

            <button className="btn btn-default" type="submit" value="Zapisz" onClick={props.onSaveFullText}>Zapisz zmiany</button>
            <button className="btn btn-default cancel" value="Anuluj" onClick={props.onCancelFullTextEdit}>Rezygnacja ze zmian</button>
        </div>
    );
}

export default Wprowadz7;
