import React, { Component } from 'react';
import Wiersz from './Wiersz';
import { kwota_display, text_to_kwota_display, text_to_number } from '../../Utils';
import api from '../../utils/api';

export default class Raport extends Component {

    constructor(props) {
        super(props);
        this.state= {raport: '', pozycje: []};
        this.zmiany= false;

        for(const f of Object.getOwnPropertyNames(Object.getPrototypeOf(this))) {
            if (f.startsWith('handle') || f.startsWith('toggle')) 
                this[f]= this[f].bind(this);
        }
    }

    zapisane() {
        return !this.zmiany;
    }

    async componentDidMount() {
        try {
            const result= await api.raport_get();
            
            // W danych wejściowych, kwoty są zapisane jako number,
            // ponieważ wprowadzane są w polach tekstowych, więc
            // pamiętamy je sformatowane tak jak wyglądają na ekranie

            const pozycje= result.data.pozycje.map(w => {
                w.kwota_a= kwota_display(w.kwota_a);
                w.kwota_b= kwota_display(w.kwota_b);
                return w;
            });
            
            const raport= result.data.raport;
            raport.all_edit= false;
            raport.zerowe= true;
            raport.formuly= false;
            raport.size= pozycje.length;

            this.setState({ raport, pozycje });

            this.zmiany= false;
        }
        catch (err) {
            window.jpk_error('Błąd przy ustalaniu pozycji zestawienia', err);
        }
    }

    obliczenie(oblicz, ten_okres) {
        if (!oblicz || oblicz.includes('(')) return '';

        let wynik= 0.00;
        let op= '+';
        // Zmienić tak aby spacje nie były potrzebne!!!
        oblicz.split(' ').forEach(x => {
            if (['+', '-', '>', '<'].includes(x))
                op= x;
            else {
                const poz= this.state.pozycje[parseInt(x)];
                x= text_to_number(ten_okres? poz.kwota_a : poz.kwota_b);
                switch(op) {
                    case '-': wynik -= x; break;
                    case '>': wynik = (wynik>0)?wynik:0; break;
                    case '<': wynik = (wynik<0)?wynik:0; break;
                    default: /* '+' */
                              wynik += x; break;
                }
            }
        });
        return wynik;
    }

    wyrazenie(zalezne, ten_okres) {
        if (!zalezne && zalezne !== 0) return;

        if (Number.isInteger(zalezne))
            zalezne= String(zalezne);

        for(let zal of zalezne.split(',')) {
            zal= parseInt(zal);
            const p= this.state.pozycje[zal];

            if (ten_okres)
                p.kwota_a= kwota_display(this.obliczenie(p.oblicz, ten_okres));
            else
                p.kwota_b= kwota_display(this.obliczenie(p.oblicz, ten_okres));

            this.wyrazenie(p.zalezne, ten_okres);
        }
    }

    handleChange(wiersz) {
        return (pole, e) => {
            wiersz[pole]= e.target.value;
            this.setState((state) => state);
            this.zmiany= true;
        };
    }

    handleBlur(wiersz) {
        return (pole, e) => {
            if (pole.startsWith('obliczenia')) {
                const formula= e.target.innerHTML.replace(/&nbsp;/g, ' ').trimEnd();
                if (formula !== wiersz.formula) {
                    wiersz.formula= formula;
                    this.zmiany= true;
                }
                wiersz.edytowana= false;
            }
            else {
                wiersz[pole]= text_to_kwota_display(e.target.value);
                if (wiersz.zalezne || wiersz.zalezne===0)
                    this.wyrazenie(wiersz.zalezne, pole==='kwota_a');
            }

            wiersz.current= false;
            this.setState((state) => state);
        };
    }

    handleFocus(wiersz) {
        return (pole, e) => {
            const e_target= e.target;
            
            // Wyrzucamy spacje oraz końcowe zera po przecinku
            let v= wiersz[pole].trim(); 
            v= v.replace(/\s/g, '').replace(',', '.');
            v= parseFloat(v);
            v= isNaN(v)? '' : v.toLocaleString('pl-PL', {useGrouping: false}); 
            
            wiersz[pole]= v;
            wiersz.org_value= wiersz[pole];
            wiersz.current= true;

            this.setState((state) => state, () => {
                e_target.select && e_target.select();
            });
        };
    }

    async handleSave() {
        // Wywoływana po kliknięciu przycisku "Zapisz" w nagłówku formularza
        try {
            // Tutaj raczej nie powinno być FormData, tylko JSON
            // Jeżeli działamy z API to komunikacja po JSON

            // let data = new FormData();
            // data.append('data', JSON.stringify(this.state.pozycje.map(w => {

            const data= this.state.pozycje.map(w => {
                return {
                    id: w.id, 
                    a: text_to_number(w.kwota_a),
                    b: text_to_number(w.kwota_b),
                    obl: this.state.raport.formuly? w.formula : '!@#'
                };
            });

            await api.raport_save(data);
            
            window.jpk_info('Zmiany zostały zapisane');

            // Przeładowanie okna z kontrolką sprawozdania w celu odświeżenia podsumowania raportu
            window.opener.location.reload(false);
            
            this.zmiany= false;
        }
        catch (err) {
            window.jpk_error('Błąd przy zapisywaniu raportu', err);
        } 
    }

    niezerowy(wiersz) {
        // Sprawdzenie czy wiersz jest niezerowy
        return this.state.raport.zerowe || wiersz.kwota_a || wiersz.kwota_b;
    }

    handleNextRow(index, kierunek) {
        if (kierunek > 0)
            while (index < this.state.pozycje.length-1) {
                index++;
                if (!this.state.pozycje[index].oblicz && !this.state.pozycje[index].kontener)
                    break;
            }
        else
            while (index > 0) {
                index--;
                if (!this.state.pozycje[index].oblicz && !this.state.pozycje[index].kontener)
                    break;
            }
        return index;
    }
    
    toggleZerowe() {
        this.setState(state => ({ raport: { ...state.raport, zerowe: !state.raport.zerowe }}));
    }

    togglePoprzedni() {
        this.setState(state => ({ raport: { ...state.raport, all_edit: !state.raport.all_edit }}));
    }

    toggleFormuly() {
        this.setState(state => ({ raport: { ...state.raport, formuly: !state.raport.formuly }}));
    }

    handleStateChange() {
        this.setState((state) => state);
    }

    render() {
        return (
            <form autoComplete="off">

                <div className="raport">

                    <label>
                        <input type="checkbox" checked={this.state.raport.zerowe} onChange={this.toggleZerowe} name="zerowe"/> Zerowe
                    </label>
                    
                    <label>
                        <input type="checkbox" checked={this.state.raport.all_edit} onChange={this.togglePoprzedni} name="poprzedni"/> Poprzedni rok
                    </label>

                    <label>
                        <input type="checkbox" checked={this.state.raport.formuly} onChange={this.toggleFormuly} name="formuly"/> Formuły obliczeń
                    </label>

                    <table>
                        <thead>
                            <tr>
                                <th className="al">Wiersz</th>
                                <th>Treść / wyszczególnienie</th>
                                {this.state.raport.formuly?
                                    <th className="formuly-kol">Formuły obliczeń</th>
                                    :
                                    <React.Fragment>
                                        <th className="ar">Bieżący okres</th>
                                        <th className="ar end">Poprzedni okres</th>
                                    </React.Fragment>
                                }
                            </tr>
                        </thead>

                        <tbody>
                            {this.state.pozycje.filter((wiersz) => this.niezerowy(wiersz)).map((wiersz, index) => 
                                <Wiersz  key={wiersz.id}
                                    raport={this.state.raport}
                                    wiersz={wiersz} 
                                    index={index} 
                                    onChange={this.handleChange(wiersz)} 
                                    onBlur={this.handleBlur(wiersz)}
                                    onFocus={this.handleFocus(wiersz)}
                                    nextRow={this.handleNextRow}
                                    onStateChange={this.handleStateChange}
                                />
                            )}
                        </tbody>
                    </table>
                </div>

            </form>
        );
    }
}
