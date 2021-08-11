import React, { Component } from 'react';
import { wyr_podatek } from '../../utils/wyroznienia';

export class PodatekWiersz extends Component {
    
    wiersz_klasy(wiersz) {
        let cls= 'tekst klu'+(wiersz.klucz.length)*10;
        cls += ' wyr'+wiersz.klucz.length;
        return cls;
    }
    
    ujemna_kwota(pole, kwota) {
        return (pole.indexOf('kwota')>=0 && kwota.indexOf('-')>=0)? 'ujemna' : '';
    }

    /**
     * Sprawdzenie czy podany wiersz główny zawiera podpozycje.
     * Jest więcej niż jedna pozycja w bloku podanej pozycji.
     * 
     * @param wiersz Wiersz, którego blok sprawdzamy
     */
    podpozycje(pozycje, wiersz) {
        return pozycje.filter(x => x.klucz[0] === wiersz.klucz[0] && !x.deleted).length>1;
    }

    readonly(raport, pozycje, wiersz, kol) {
        return (wiersz.kontener || wiersz.oblicz || (wiersz.klucz.length===1 && (kol.indexOf('pp')===0 || this.podpozycje(pozycje, wiersz))))? 'readonly' : '';
    }

    input_klasy(raport, wiersz, pole, podstawa, ...reszta) {
        const kwota= wiersz[pole];

        const align= (pole==='nazwa')?pole:'ar';
        let tklas= [align];

        if (pole.startsWith('kwota')) {
            const ujemna= this.ujemna_kwota(pole, kwota);
            if (ujemna)
                tklas.push(ujemna);
        }

        if (wiersz.kontener)
            tklas.push('kontener');

        const cc= this.curr_class(wiersz);
        if (cc) 
            tklas.push(cc);
        
        tklas.push(reszta);
        if (wiersz.klucz.length===1 && podstawa)
            tklas.push('wyrUSB kontener');

        return tklas.join(' ');
        //return `${align} ${this.ujemna_kwota(pole, kwota)} ${wiersz.kontener?'kontener':''} ${this.curr_class(wiersz)} ${reszta} ${(wiersz.klucz.length===1 && podstawa)?'wyrUSB kontener':''}`;
    }

    // Przy ALL_EDIT tab przenosi nas między obu kolumnami (brak tabIndex), 
    // wpp tab tylko w pierwszej kolumnie (jak Enter)
    tabindex(raport, index, ten_okres) {
        return raport.all_edit? void 0 : ten_okres? index : -1;
    }

    klucz(wiersz) { 
        return wiersz.klucz.replace('Aktywa_', '').replace('Pasywa_', '').replace(/_/g, ' ');
    }

    curr_class(wiersz) {
        return wiersz.current? 'curr':'';
    }

    handleChange(pole) {
        return (e) => {
            this.props.onChange(pole, e);
        };
    }

    handleBlur(pole) {
        return (e) => {
            this.props.onBlur(pole, e);
        };
    }

    handleFocus(pole) {
        return (e) => {
            this.props.onFocus(pole, e);
        };
    }
    
    onKeyPress(wiersz, pole, index) {
        // Reakcja na Enter, Escape i strzałki dół/góra
        return (e) => { 
            if (e.key === 'Escape') {
                e.target.value= wiersz.org_value;
                e.target.select();
                return;
            }

            let row= -1;
            if (e.key === 'Enter' || e.key === 'ArrowDown')
                row= (index+1 < this.props.raport.size)?index+1:index;

            if (e.key === 'ArrowUp') 
                row= (index > 0)? index-1 : 0;

            if (row !== -1) {
                e.preventDefault();
                const el= document.getElementById(pole+row);
                if (el) el.focus();
            }
        };
    }

    nazwaFocus(wiersz) {
        return () => {
            wiersz.edytowana= true;
            this.props.onStateChange();
        };
    }

    nazwa(raport, wiersz, podstawa, index) {
        const pole= 'nazwa';
        return (
            (wiersz.edytowana)?
                <td className={this.wiersz_klasy(wiersz, pole)}>
                    <div 
                        autoComplete="off"
                        id={pole+index}
                        tabIndex={this.tabindex(raport, index, false)}
                        //readOnly={this.readonly(raport, wiersz, pole)}
                        className={this.input_klasy(raport, wiersz, pole, podstawa)}
                        onChange={this.handleChange(pole)}
                        onBlur={this.handleBlur(pole)}
                        onFocus={this.handleFocus(pole)}
                        onKeyPress={this.onKeyPress(wiersz, pole, index)}
                        onKeyDown={this.onKeyPress(wiersz, pole, index)}
                        contentEditable="true"
                        ref={(input) => input && input.focus()}
                    >
                        {wiersz[pole]}
                    </div>
                </td>
                :
                <td className={this.wiersz_klasy(wiersz, pole)} onClick={this.nazwaFocus(wiersz)}>
                    {wiersz.nazwa}
                </td>
        );
    }

    input(raport, pozycje, wiersz, podstawa, index, pole) {
        let td_class= (pole.indexOf('kwota')>=0)?'kwoty ar' : 'pp';

        return (
            (wiersz.klucz.length===1 && pole.indexOf('pp')===0)?
                <td> </td>
                :
                <td className={td_class}>
                    <input type="text" 
                        autoComplete="off"
                        id={pole+index}
                        tabIndex={this.tabindex(raport, index, false)}
                        readOnly={this.readonly(raport, pozycje, wiersz, pole)}
                        className={this.input_klasy(raport, wiersz, pole, podstawa)}
                        onChange={this.handleChange(pole)}
                        onBlur={this.handleBlur(pole)}
                        onFocus={this.handleFocus(pole)}
                        onKeyPress={this.onKeyPress(wiersz, pole, index)}
                        onKeyDown={this.onKeyPress(wiersz, pole, index)}
                        value={wiersz[pole]}
                    />
                </td>
        );
    }

    render() {
        const {raport, pozycje, wiersz, index, podstawa} = this.props;

        return (
            <tr className={[wyr_podatek(wiersz, podstawa), this.curr_class(wiersz)].join(' ').trim()}>
                <td className="tekst klucz">{this.klucz(wiersz)}</td>
                {this.nazwa(raport, wiersz, podstawa, index)}

                {this.input(raport, pozycje, wiersz, podstawa, index, 'kwota_a')}
                {this.props.kapitalowe && this.input(raport, pozycje, wiersz, podstawa, index, 'kwota_b')}
                {this.props.kapitalowe && this.input(raport, pozycje, wiersz, podstawa, index, 'kwota_c')}

                {this.props.podstawa && this.input(raport, pozycje, wiersz, podstawa, index, 'ppa')}
                {this.props.podstawa && this.input(raport, pozycje, wiersz, podstawa, index, 'ppb')}
                {this.props.podstawa && this.input(raport, pozycje, wiersz, podstawa, index, 'ppc')}
                {this.props.podstawa && this.input(raport, pozycje, wiersz, podstawa, index, 'ppd')}

                {this.props.poprzedni && this.input(raport, pozycje, wiersz, podstawa, index, '_kwota_a')}
            </tr>
        );
    }
}
