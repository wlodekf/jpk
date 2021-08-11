import React, { Component } from 'react';
import { skrotTekstu } from '../../utils/utils';

/**
 * Informacja o uszczegółowieniu widoczna w głównym formularzu wprowadzenia.
 * Jest to skrót, tylko dwa początkowe akapity uszczegółowienia tak aby
 * główny formularz wprowadzenia nie był za długi bo wtedy trudno byłoby
 * się po nim poruszać.
 * 
 * Pełny widok uszczegółowienia i ewentualna edycja wyświetlane są w 
 * osobnym formularzu.
 */
export default class UszczegolowienieSkrot extends Component {

    p8_opis(poz) {
        return poz.p8_opis.split('\n').map((a, lp) => 
            <React.Fragment key={lp}>
                {(lp && a.length>0)?<br/>:''}
                {a}
            </React.Fragment>
        );
    }

    pozycja(props) {
        const onP8Show= (e) => props.onP8Show(e, props.lp);
        /*
        if (props.len>3) {
            return (
                <a href="/" className="list-group-item" onClick={onP8Show}>{props.lp+1}. {props.p8_nazwa}</a>
            );
        }
        */
        return (
            <a href="/" className="list-group-item" onClick={onP8Show}>
                <h4 className="list-group-item-heading nag">{props.p8_nazwa}</h4>
                {skrotTekstu(props.p8_opis)}

                {/*
                <p className="list-group-item-text">{this.p8_opis(props)}</p>
                */}
            </a>
        );
    }

    render() {
        return (
            this.pozycja({...this.props, ...this.props.poz})
        );
    }
}
