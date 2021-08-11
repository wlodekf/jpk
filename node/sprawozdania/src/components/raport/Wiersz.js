import React, { Component } from 'react';
import { wyroznienie } from '../../utils/wyroznienia';

// Sprawdzenie czy wiersz zawiera obliczenia (sumowanie,odejmowanie) robione online w JS
const obliczenia= (wiersz) => wiersz && wiersz.oblicz && !wiersz.oblicz.includes('(');

// Klasy dla komórki tabeli w danej kolumnie
const td_klasy= (wiersz, pole) => {
    let cls= ['tekst'];
    if (pole==='nazwa')
        cls.push('klu'+wiersz.klu1.length*10);
    cls.push('wyr'+wiersz.klu1.length);
    if (obliczenia(wiersz)) 
        cls.push('oblicz');
    return cls.join(' ');
};

// Klasa dla komórek ujemnych wartości
const ujemna_kwota= (kwota) => (kwota.indexOf('-')>=0)? 'ujemna' : '';

// Klasa dla wierszy obliczanych
const oblicz= (wiersz) => obliczenia(wiersz)?'oblicz':'';



// Wiersz tabeli raportu
export default class Wiersz extends Component {

    onKeyPress(wiersz, kolumna, index, nextRow) {
        // Reakcja na Enter i strzałki dół/góra
        return (e) => { 
            if (e.key === 'Escape') {
                e.target.value= wiersz.org_value;
                e.target.select();
                return;
            }

            let row= -1;
            if (e.key === 'Enter' || e.key === 'ArrowDown')
                row= nextRow(index, +1);
                //(index+1 < this.props.raport.size)?index+1:index;

            if (e.key === 'ArrowUp')
                row= nextRow(index, -1);
                // (index > 0)? index-1 : 0;

            if (row !== -1) {
                e.preventDefault();
                document.getElementById(kolumna+row).focus();
            }
        };
    }

    readonly(raport, wiersz, kol) {
        return ((kol==='b' && !raport.all_edit) || wiersz.kontener || obliczenia(wiersz))? 'readonly' : '';
    }

    klasy(raport, wiersz, pole, ...reszta) {
        return `ar ${ujemna_kwota(wiersz[pole])} ${(pole==='obliczenia')?'':wyroznienie(raport.element, wiersz)} ${wiersz.kontener?'kontener':''} ${this.curr_class(wiersz)} ${oblicz(wiersz)} ${reszta}`;
    }

    // Przy ALL_EDIT tab przenosi nas między obu kolumnami (brak tabIndex), 
    // wpp tab tylko w pierwszej kolumnie (jak Enter)
    tabindex(raport, index, ten_okres) {
        return raport.all_edit? void 0 : ten_okres? index : -1;
    }

    klucz(wiersz) {
        return wiersz.el.replace('Aktywa_', '').replace('Pasywa_', '').replace(/_/g, ' ');
    }

    curr_class(wiersz) {
        return wiersz.current? 'curr':'';
    }

    disabled(wiersz) {
        return (obliczenia(wiersz.oblicz) || wiersz.kontener)?'disabled':null;
    }

    onChange(pole) {
        // Po zmianie wartości podanego pola (kwoty w którejś z kolumn)
        return (e) => {
            this.props.onChange(pole, e);
        };
    }

    onFocus(pole) {
        return (e) => {
            this.props.onFocus(pole, e);
        };
    }

    onBlur(pole) {
        return (e) => {
            this.props.onBlur(pole, e);
        };
    }

    kolumna(kol) {
        const {raport, wiersz, index, nextRow} = this.props;
        const pole= 'kwota_'+kol;

        return (
            <input type="text"
                id={kol+index} 
                tabIndex={this.tabindex(raport, index, kol==='a')} 
                readOnly={this.readonly(raport, wiersz, kol)} 
                disabled={this.disabled(wiersz)}
                className={this.klasy(raport, wiersz, pole)}
                onChange={this.onChange(pole)} 
                onBlur={this.onBlur(pole)}
                onFocus={this.onFocus(pole)}
                onKeyPress={this.onKeyPress(wiersz, kol, index, nextRow)}
                onKeyDown={this.onKeyPress(wiersz, kol, index, nextRow)}
                value= {wiersz[pole]}
            />
        );
    }

    oblFocus(wiersz) {
        return () => {
            wiersz.edytowana= true;
            this.props.onStateChange();
        };
    }

    // Kolumna z formułami.
    formuly(raport, wiersz) {
        const {index} = this.props;
        const pole= 'obliczenia';
        return (
            (wiersz.edytowana)?
                <td className={td_klasy(wiersz, pole)}>
                    <div 
                        autoComplete="off"
                        id={pole+index}
                        tabIndex={this.tabindex(raport, index, false)}
                        //readOnly={this.readonly(raport, wiersz, pole)}
                        // className={this.klasy(raport, wiersz, pole)}
                        onChange={this.onChange(pole)} 
                        onBlur={this.onBlur(pole)}
                        onFocus={this.onFocus(pole)}
                        // onKeyPress={this.onKeyPress(wiersz, kol, index, nextRow)}
                        // onKeyDown={this.onKeyPress(wiersz, kol, index, nextRow)}

                        contentEditable="true"
                        ref={(input) => input && input.focus()}
                    >
                        {wiersz.formula}
                    </div>
                </td>
                :
                <td className={td_klasy(wiersz, pole)} onClick={this.oblFocus(wiersz)}>
                    {wiersz.formula}
                </td>
        );
    }

    // Kolumny z kwotami
    kwoty() {
        return (
            <React.Fragment>
                <td className="kwoty">
                    {this.kolumna('a')}
                </td>
                <td className="kwoty end">
                    {this.kolumna('b')}
                </td>
            </React.Fragment>        
        );
    }

    render() {
        const {raport, wiersz} = this.props;

        return (
            <tr className={[wyroznienie(raport.element, wiersz), this.curr_class(wiersz), oblicz(wiersz), wiersz.kontener?' oblicz':''].join(' ').trim()}>

                <td className="tekst klucz">{this.klucz(wiersz)}</td>
                <td className={td_klasy(wiersz, 'nazwa')}>{wiersz.nazwa}</td>

                {raport.formuly? this.formuly(raport, wiersz) : this.kwoty()}
            </tr>
        );
    }
}
