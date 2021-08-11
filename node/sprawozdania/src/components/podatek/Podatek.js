import React, { Component } from 'react';
import { PodatekWiersz } from './PodatekWiersz';
import { kwota_display, text_to_kwota_display, text_to_number } from '../../Utils';
import api from '../../utils/api';

/*
    Do zrobienia
    1. zamiast kwota_a, b, c, rb_lacznie, rb_kapitalowe, rb_inne, ...
    2. sumowanie podpozycji do pozycji
*/
class Podatek extends Component {

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

    refresh(result) {
        // W danych wejściowych, kwoty są zapisane jako number,
        // ponieważ wprowadzane są w polach tekstowych, więc
        // pamiętamy je sformatowane tak jak wyglądają na ekranie
        // Hm, czy to dobry pomysł?
        const pozycje= result.data.pozycje.map(w => {
            w.kwota_a= kwota_display(w.kwota_a);
            w.kwota_b= kwota_display(w.kwota_b);
            w.kwota_c= kwota_display(w.kwota_c);
            w._kwota_a= kwota_display(w._kwota_a);
            return w;
        });

        let podstawa= false;
        let kapitalowe= false;
        let poprzedni= false;

        pozycje.forEach((e) => {
            if (e.klucz.length > 1)
                podstawa= true;
            if (e.kwota_b || e.kwota_c)
                kapitalowe= true;
            if (e._kwota_a)
                poprzedni= true;
        });

        const raport= result.data.raport;
        raport.all_edit= true;
        raport.zerowe= true;
        raport.size= pozycje.length;

        this.setState({ raport, pozycje, kapitalowe, poprzedni, podstawa });

        this.zmiany= false;        
    }

    async componentDidMount() {
        try {
            // Pobranie danych pozycji tabeli
            const result= await api.podatek_get();
            this.refresh(result);
        }
        catch (err) {
            console.error('Błąd przy ustalaniu pozycji rozliczenia różnicy', err);            
            window.jpk_error('Błąd przy ustalaniu pozycji rozliczenia różnicy', err);
        }
    }

    async handleSave() {
        try {
            let data = new FormData();
            
            data.append('data', JSON.stringify(this.state.pozycje.map(w => {
                return {
                    id: w.id, 
                    a: text_to_number(w.kwota_a),
                    b: text_to_number(w.kwota_b),
                    c: text_to_number(w.kwota_c),
                    ppa: w.ppa,
                    ppb: w.ppb,
                    ppc: w.ppc,
                    ppd: w.ppd,
                    _a: text_to_number(w._kwota_a),
                    klucz: w.klucz,
                    nazwa: w.nazwa,
                    deleted: w.deleted
                };
            })));
            
            const result= await api.podatek_save(data);
            this.refresh(result);

            window.jpk_info('Zmiany zostały zapisane');

            // Przeładowanie okna z kontrolką sprawozdania w celu odświeżenia podsumowania raportu
            window.opener.location.reload(false);

            this.zmiany= false;
        }
        catch (err) {
            window.jpk_error('Błąd przy zapisywaniu rozliczenia różnicy', err);
        }
    }

    obliczenie(oblicz, kolumna) {
        // Pozycja obliczana a nie wprowadzana
        if (!oblicz) return '';

        let wynik= 0.00;
        let op= '+';

        oblicz.split(' ').forEach(x => {
            if (['+', '-'].includes(x))
                op= x;
            else {
                const poz= this.state.pozycje[parseInt(x)];
                x= text_to_number(poz[kolumna]);
                wynik += (op==='+')?x:-x;
            }
        });
        return wynik;
    }

    wyrazenie(zalezne, kolumna) {
        if (!zalezne) return;

        zalezne= parseInt(zalezne);
        const p= this.state.pozycje[zalezne];

        switch(kolumna) {
        case 'kwota_a': p.kwota_a= kwota_display(this.obliczenie(p.oblicz, kolumna)); break;
        case 'kwota_b': p.kwota_b= kwota_display(this.obliczenie(p.oblicz, kolumna)); break;
        case 'kwota_c': p.kwota_c= kwota_display(this.obliczenie(p.oblicz, kolumna)); break;
        default:
        }

        this.wyrazenie(p.zalezne, kolumna);
    }

    handleChange(wiersz) {
        return (pole, e) => {
            wiersz[pole]= e.target.value;
            this.setState((state) => state);
            this.zmiany= true;
        };
    }

    /**
     * Obliczenie sum bloku podanego wiersza i wpisanie ich w odpowiednią pozycję.
     * @param {*} wiersz 
     */
    sumowanie(wiersz) {
        const grupa= wiersz.klucz[0];
        // Podpozycje mogą być tylko w grupach B-I
        if (grupa === 'A' || grupa > 'I') return;

        let suma= [0, 0, 0, 0]; // sumy kolumn kwotowych
        let ile= 0; // liczba pozycji w grupie
        let glowna; // wiersz główny
        
        for (const i in this.state.pozycje) {
            const poz= this.state.pozycje[i];
            // sumowanie pozycji danej grupy i ustalanie głównego wiersza
            if (poz.klucz[0] === grupa && !poz.deleted) {
                ile += 1;
                if (poz.klucz.length === 1)
                    glowna= poz;
                if (poz.klucz.length > 1) {
                    suma[0] += text_to_number(poz.kwota_a);
                    suma[1] += text_to_number(poz.kwota_b);
                    suma[2] += text_to_number(poz.kwota_c);
                    suma[3] += text_to_number(poz._kwota_a);
                }
            }
        }

        if (ile !== 1) {
            // Wpisanie sum (state musi się zmienić)
            glowna.kwota_a= text_to_kwota_display(''+suma[0]);
            glowna.kwota_b= text_to_kwota_display(''+suma[1]);
            glowna.kwota_c= text_to_kwota_display(''+suma[2]);
            glowna._kwota_a= text_to_kwota_display(''+suma[3]);
        }
    }

    handleBlur(wiersz) {
        return (pole, e) => {
            if (pole.startsWith('nazwa')) {
                const nazwa= e.target.innerHTML.replace(/&nbsp;/g, ' ').trimEnd();
                if (nazwa !== wiersz[pole]) {
                    wiersz[pole]= nazwa;
                    this.zmiany= true;
                }
                wiersz.edytowana= false;
            }
            else {
                wiersz[pole]= (pole.indexOf('kwota')>=0)?text_to_kwota_display(e.target.value) : e.target.value;
                if (wiersz.zalezne)
                    this.wyrazenie(wiersz.zalezne, false);

                this.sumowanie(wiersz);
            }

            wiersz.current= false;
            this.setState((state) => state);
        };
    }

    handleFocus(wiersz) {
        return (pole, e) => {
            const e_target= e.target;
            
            // Wyrzucamy spacje oraz końcowe zera po przecinku
            let v= wiersz[pole];
            if (v) v= v.trim(); 

            if (pole.indexOf('kwota')>=0) {
                v= v.replace(/\s/g, '').replace(',', '.');
                v= parseFloat(v);
                v= isNaN(v)? '' : v.toLocaleString('pl-PL', {useGrouping: false}); 
            }

            wiersz[pole]= v;
            wiersz.org_value= v;
            wiersz.current= true;

            this.setState(() => {return {last: wiersz}}, () => {
                e_target.select && e_target.select();
            });
        };
    }

    // Wyświetlenie wierszy niezerowych lub obowiązkowych
    niezerowy(wiersz) { 
        return this.state.raport.zerowe || wiersz.kwota_a || wiersz.kwota_b || wiersz.kwota_c;
    }

    toggleKapitalowe() {
        this.setState({kapitalowe: !this.state.kapitalowe});
    }

    togglePoprzedni() {
        this.setState({poprzedni: !this.state.poprzedni});
    }

    pozycjaUzytkownika(options) {
        return Object.assign({
            element: 'PozycjaUzytkownika',
            id: 0,
            klu1: '',
            klucz: '',
            kontener: false,
            kwota_a: '',
            kwota_b: '',
            kwota_c: '',
            nazwa: '',
            org_value: '',
            ppa: '',
            ppb: '',
            ppc: '',
            ppd: '',
            _kwota_a: '',
            _kwota_b: '',
            _kwota_c: ''
        }, 
        options);
    }

    handleDodajPozycje() {

        if (this.state.last) {
            // 1. trzeba ustalić, w którym bloku jesteśmy/dodajemy
            // 2. następnie trzeba znaleźć przedostatnią pozycję (jeżeli jest)
            // 3. ustalić numer nowej pozycji

            //const last= this.state.last;

            const block= this.state.last.klu1[0];
            let isx= false;

            let pop; // indeks pozycji poprzedzającej dodawaną
            for (const i in this.state.pozycje) {
                const poz= this.state.pozycje[i];
                if (poz.klu1[0] === block) {
                    if (poz.klu1.endsWith('X')) {
                        if (!poz.deleted)
                            isx= true;
                    }
                    else
                    if (!poz.deleted)
                        pop= Number(i);
                }
            }

            const poz= this.state.pozycje[pop];
            const nr= (poz.klucz.length === 1)? 1 : Number.parseInt(poz.klucz.substring(1), 16)+1;
            const klucz= block+Number(nr).toString(16).toUpperCase();
            const nowa= this.pozycjaUzytkownika({klu1: klucz, klucz});

            // Dodanie nowej podpozycji
            this.state.pozycje.splice(pop+1, 0, nowa);

            // Ewentualne dodanie podpozycji "inne"
            if (!isx) {
                this.state.pozycje.splice(pop+2, 0, 
                    this.pozycjaUzytkownika({
                        klu1: block+'X',
                        klucz: block+'X',
                        nazwa: 'inne',
                    })
                );
            }

            this.zmiany= true;
            this.setState((state)=>state);
        }
    }

    handleUsunPozycje() {
        if (this.state.last) {
            const last= this.state.last;
            last.deleted= true;
            const block= last.klucz[0];

            // Jeżeli nowo dodana (nie ma id) to usuwać z tablicy
            if (!last.id) {
                const l= this.state.pozycje.findIndex(x => x===last);
                this.state.pozycje.splice(l, 1);
            }
            
            let nr= 0;
            let x;
            
            // Przenumerowanie kluczy pozycji (usuwanie dziur w numeracji)
            this.state.pozycje.forEach((v, index) => {
                if (v.klucz[0] === block && v.klucz.length > 1 && !v.deleted && !v.klucz.endsWith('X'))
                {
                    v.klucz= block + Number(++nr).toString(16).toUpperCase();
                    v.klu1= v.klucz;
                }
                if (v.klucz[0] === block && v.klucz.endsWith('X'))
                    x= index;
            });
            
            // Po usunięciu ostatniej pozycji numerowanej usunąć pozycję końcowa "X"
            if (nr===0 && x) {
                const pozycjaX= this.state.pozycje[x];
                pozycjaX.deleted= true;
            }
            
            this.sumowanie(last);

            this.zmiany= true;
            this.setState((state) => state);
        }
    }

    usunButton() {
        if (this.state.last && this.state.last.klucz.length>1 && !this.state.last.klucz.endsWith('X'))
            return (
                <button type="button" className="btn btn-xs btn-default btn-pozycji" onClick={this.handleUsunPozycje}>
                    <span className="glyphicon glyphicon-remove iko" aria-hidden="true"></span>
                    Usuń pozycję
                </button>
            );
    }

    dodajButton() {
        if (this.state.last && 'AJK'.indexOf(this.state.last.klucz[0])<0)
            return (
                <button type="button" className="btn btn-xs btn-default btn-pozycji" onClick={this.handleDodajPozycje}>
                    <span className="glyphicon glyphicon-plus iko" aria-hidden="true"></span>
                    Dodaj pozycję
                </button>
            );
    }

    handleStateChange() {
        this.setState((state) => state);
    }

    render() {
        return (
            <div className="raport">
                <label>
                    <input type="checkbox" checked={this.state.kapitalowe} onChange={this.toggleKapitalowe} name="kapitalowe"/> Kapitałowe/inne
                </label>
                
                <label>
                    <input type="checkbox" checked={this.state.poprzedni} onChange={this.togglePoprzedni} name="poprzedni"/> Poprzedni rok
                </label>
                
                {this.dodajButton()}
                {this.usunButton()}

                <table className="tpod">
                    <thead>
                        <tr>
                            <th rowSpan="2">Lp</th>
                            <th rowSpan="2">Treść / wyszczególnienie</th>

                            <th colSpan={this.state.kapitalowe?'3':'1'} className={!this.state.kapitalowe && 'ar'}>Bieżący rok</th>

                            {this.state.podstawa && <th colSpan="4">Podstawa prawna</th>}

                            {this.state.poprzedni &&
                                <th rowSpan="2" className="ar">Poprzedni rok<br/>Łącznie</th>
                            }
                        </tr>

                        <tr>
                            <th className="ar">Łącznie</th>
                            {this.state.kapitalowe && <th className="ar">z zysków kapitałowych</th>}
                            {this.state.kapitalowe && <th className="ar">z innych źródeł</th>}

                            {this.state.podstawa && <th>Art.</th>}
                            {this.state.podstawa && <th>Ust.</th>}
                            {this.state.podstawa && <th>Pkt</th>}
                            {this.state.podstawa && <th>Lit.</th>}
                        </tr>

                    </thead>
                    <tbody>
                        {this.state.pozycje.filter((wiersz) => this.niezerowy(wiersz) && !wiersz.deleted).map((wiersz, index) => 
                            <PodatekWiersz  key={index}
                                raport={this.state.raport}
                                pozycje={this.state.pozycje}
                                wiersz={wiersz} 
                                index={index}
                                kapitalowe={this.state.kapitalowe}
                                podstawa={this.state.podstawa}
                                poprzedni={this.state.poprzedni}
                                onChange={this.handleChange(wiersz)}
                                onBlur={this.handleBlur(wiersz)}
                                onFocus={this.handleFocus(wiersz)}
                                onStateChange={this.handleStateChange}
                            />
                        )}
                    </tbody>
                </table>
            </div>
        );
    }
}

export default Podatek;
