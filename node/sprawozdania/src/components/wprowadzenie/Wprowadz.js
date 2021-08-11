import React, { Component } from 'react';
import api from '../../utils/api';

import WprSekcja from './WprSekcja';
import Wprowadz1 from './Wprowadz1';
import Wprowadz2 from './Wprowadz2';
import Wprowadz3 from './Wprowadz3';
import Wprowadz4 from './Wprowadz4';
import Wprowadz5 from './Wprowadz5';
import Wprowadz6 from './Wprowadz6';
import Wprowadz7, { FullText, FullTextEdit } from './Wprowadz7';
import Wprowadz8 from './Wprowadz8';

// Lazy loading komponentu - komponent moduł jest ładowany dopiero gdy i jeśli będzie użyty
// czyli w tym przypadku gdy nastąpi przejście do edycji uszczegółowienia
// W tym przypadku nie ma to zbyt wielkiego sensu bo komponent/moduł jest mały
const Uszczegolowienie= React.lazy(() => import('./Uszczegolowienie'));

const SEKCJE= [
    [],
    [Wprowadz1, 'Dane identyfikujące jednostkę', 
        'Dane identyfikujące jednostkę. Firma, siedziba albo miejsce zamieszkania.'],
    [Wprowadz2, 'Czas trwania działalności', 
        'Czas trwania działalności jednostki, <b>jeżeli jest ograniczony</b>. Zakres dat od - do przy czym data do może mieć charakter opisowy.'],
    [Wprowadz3, 'Okres sprawozdania' , 
        'Wskazanie okresu objętego sprawozdaniem finansowym. Zakres dat od - do z uwzględnieniem ograniczeń dla elektronicznych sprawozdań finansowych.'],
    [Wprowadz4, 'Dane łączne', 
        'Wskazanie, że sprawozdanie finansowe zawiera dane łączne, jeżeli w skład jednostki wchodzą wewnętrzne jednostki organizacyjne sporządzające samodzielne sprawozdania finansowe.'],
    [Wprowadz5, 'Założenie kontynuacji działalności', ''],
    [Wprowadz6, 'Sprawozdanie po połączeniu', ''],
    [Wprowadz7, 'Polityka rachunkowości', '']
];

const ETYKIETY= {
    'p7_zasady': 'Omówienie przyjętych zasad (polityki) rachunkowości, w zakresie w jakim ustawa pozostawia jednostce prawo wyboru',
    'p7_wycena': 'Omówienie przyjętej metody wyceny aktywów i pasywów (także amortyzacji)',
    'p7_wynik': 'Omówienie przyjętych zasad ustalenia wyniku finansowego',
    'p7_spraw': 'Omówienie sposobu sporządzenia sprawozdania finansowego'
};

class Wprowadz extends Component {

    constructor(props) {
        super(props);

        this.state= {
            readonly: true,
            view: 'calosc', 
            p8: [],
        };
        this.zmiany= false;
        this.old_y= null;
        this.new_y= null;

        for(const f of Object.getOwnPropertyNames(Object.getPrototypeOf(this))) {
            if (f.startsWith('handle')) this[f]= this[f].bind(this);
        }
    }

    zapisane() {
        return !this.zmiany;
    }

    handleChange(e) {
        // preventing checkbox state change on readonly state
        if (e.target.type === 'checkbox' && this.state.readonly)
            return;

        let change = { [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value };
        if (e.target.name === 'p8_opis')
            Object.assign(change, {tah: e.target.scrollHeight});

        this.zmiany= true;

        this.setState(change);
    }

    handleP8Change(e, lp) {
        const et_name= e.target.name;
        const et_value= e.target.value;
        const et_type= e.target.type;
        const et_checked= e.target.checked;

        this.setState((state) => {
            const p8poz= state.p8[lp];
            p8poz[et_name] = et_type === 'checkbox' ? et_checked : et_value;
            return {p8: state.p8};
        });
    }

    handleP8Show(e, lp) {
        this.old_y= window.pageYOffset;
        e.preventDefault();
        this.new_y= 0;

        this.setState((state) => {
            const { p8_nazwa, p8_opis } = state.p8[lp];
            return {view: 'uszczegolowienie', p8_lp: lp, p8_nazwa, p8_opis};
        });
    }

    handleP8Back(e) {
        this.new_y= this.old_y;
        this.old_y= void 0;
        e.preventDefault();

        this.setState(() => {
            this.setState({view: 'calosc', lp: -1});
        });
    }

    handleP8Save(e) {
        e.preventDefault();
        this.new_y= 0;
        this.zmiany= false;

        this.setState((state) => {
            const {p8_nazwa, p8_opis, p8}= state;
            let p8_lp= state.p8_lp;

            if (p8_lp<0) {
                p8.push({p8_id: 0, p8_nazwa, p8_opis});
                p8_lp= p8.length-1;
            }
            else
                Object.assign(p8[p8_lp], {p8_nazwa, p8_opis});

            return {p8, p8_lp, readonly: true};
        }, 
        () => {
            this.onP8Save();
        });
    }
    
    handleP8Edit(e) {
        this.new_y= 0;
        e.preventDefault();

        this.setState(() => {
            return {readonly: false};
        });
    }

    handleP8Usun(e) {
        this.new_y= this.old_y;
        this.old_y= void 0;
        e.preventDefault();
        let p8_poz= void 0;

        this.setState(({p8_lp, p8}) => {
            if (p8_lp>=0) {
                p8_poz= p8.splice(p8_lp, 1);
            }

            return {p8, view: 'calosc'};
        },
        () => {
            api.p8_del(p8_poz);
        });
    }

    handleP8Anuluj(e) {
        this.new_y= 0;
        e.preventDefault();

        this.setState((state) => {
            const lp= this.state.p8_lp;
            if (lp>=0) {
                const { p8_nazwa, p8_opis } = state.p8[lp];
                this.setState({readonly: true, p8_nazwa, p8_opis});
            }
            else {
                this.new_y= this.old_y;
                this.setState({readonly: true, view: 'calosc'});
            }
        });
    }

    handleDodaj(e) {
        // Przejście do edycji nowej pozycji uszczegółowienia
        this.old_y= window.pageYOffset;
        this.new_y= 0;
        e.preventDefault();
        this.setState(() => {
            return {p8_lp: -1, p8_nazwa: '', p8_opis: '', view: 'uszczegolowienie', readonly: false};
        });
    }
    
    uszczegolowienie() {
        return (
            <React.Suspense fallback={<div>Loading ...</div>}>
                <Uszczegolowienie 
                    form={this.state}
                    onP8Edit={this.handleP8Edit}
                    onP8Back={this.handleP8Back}
                    onP8Save={this.handleP8Save}
                    onP8Usun={this.handleP8Usun}
                    onP8Anuluj={this.handleP8Anuluj}
                    onMount={this.handleMount}
                />
            </React.Suspense>
        );
    }

    handleFullText(nazwa) {
        return (e) => {
            e.preventDefault();
            this.old_y= window.pageYOffset;
            this.new_y= 0;
            this.setState(() => {
                //const txt= state[nazwa];
                return {view: 'full_text', pole: nazwa};
            });
        };
    }

    handleFullTextEdit(e) {
        this.new_y= 0;
        e.preventDefault();
        this.zmiany= false;
        this.setState(() => {
            return {view: 'full_text_edit', readonly: false};
        });
    }

    handleFullTextSave(e) {
        this.new_y= 0;

        e.preventDefault();
        this.onSave(e);
        
        this.setState(() => {
            return {view: 'full_text', readonly: true, tah: void 0};
        });

        this.zmiany= false;
    }

    handleFullTextBack(e) {
        this.new_y= this.old_y;
        this.old_y= void 0;
        e.preventDefault();
        this.setState(() => {
            this.setState({view: 'calosc', tah: void 0});
        });
    }

    handleCancelFullTextEdit(e) {
        e.preventDefault();
        this.new_y= 0;
        this.readData({view: 'full_text', readonly: true, tah: void 0});
    }

    full_text() {
        return (
            <FullText pole={this.state.pole} 
                etykieta={ETYKIETY[this.state.pole]} 
                form={this.state} 
                onFullTextEdit={this.handleFullTextEdit}
                onFullTextBack={this.handleFullTextBack}
            />
        );
    }

    handleMount(nazwa) {
        this.setState({tah: document.getElementById(nazwa).scrollHeight});
    }

    full_text_edit() {
        return (
            <FullTextEdit 
                pole={this.state.pole}
                etykieta={ETYKIETY[this.state.pole]}
                form={this.state}
                onSaveFullText={this.handleFullTextSave}
                onCancelFullTextEdit={this.handleCancelFullTextEdit}
                onMount={this.handleMount}
            />
        );
    }

    view() {
        let v= null;
        this.zmiany= false;
        switch(this.state.view) {
        case 'uszczegolowienie': v= this.uszczegolowienie(); break;
        case 'full_text': v= this.full_text(); break;
        case 'full_text_edit': v= this.full_text_edit(); break;            
        case 'sekcja': v= this.P(this.state.num); break;
        default:
            v= this.calosc();
        }
        return v;
    }

    render() {
        return (
            <div className="panel-body">
                <form onChange={this.handleChange} autoComplete="off">
                    {this.view()}
                </form>
            </div>
        );
    }

    componentDidMount() {
        this.readData({});
    }

    async readData(newState) {
        try {
            const result= await api.wprowadz_get();
            const form= result.data.form;
            this.setState({...form, ...newState});
        }
        catch (err) {
            window.jpk_error('Błąd przy ustalaniu danych wprowadzenia', err);
        }
    }

    onSave() {
        let data = new FormData();
        let d= JSON.stringify(this.state);
        data.append('data', d);
        this.zmiany= false;

        api.wprowadz_save(data)
            .catch(errors => console.error('Błąd przy zapisywaniu wprowadzenia', errors));        
    }

    onP8Save() {
        const p8_lp= this.state.p8_lp;
        const poz= this.state.p8[p8_lp];

        if (poz.p8_id)
            api.p8_save(poz);
        else
            api.p8_save(poz);
    }

    handleSectionEdit(e, num) {
        this.old_y= window.pageYOffset;
        this.new_y= 0;
        console.log('handleSectionEdit', this);
        this.setState({view: 'sekcja', num, readonly: false});
    }

    handleZapisz(e) {
        this.new_y= this.old_y;
        this.old_y= void 0;

        e.preventDefault();

        this.onSave(e);

        this.setState(() => {
            return {view: 'calosc', readonly: true};
        });
    }

    handleCancelEdit(e) {
        e.preventDefault();
        this.new_y= this.old_y;
        this.old_y= void 0;
        this.readData({view: 'calosc', readonly: true});
    }

    componentDidUpdate() { 
        if (this.new_y !== undefined) {
            window.scrollTo(0, this.new_y);
            this.new_y= void 0;
        }
    }

    P(i) {
        const [Sekcja, title, wstep]= SEKCJE[i];

        return (
            <WprSekcja num={`${i}`} 
                title={title}
                onSectionEdit={this.handleSectionEdit}
                onZapisz={this.handleZapisz}
                onCancelEdit={this.handleCancelEdit}
                readOnly={this.state.readonly}>

                <div className="wstep" 
                    dangerouslySetInnerHTML={{__html: wstep}}>
                </div>

                <Sekcja form={this.state} 
                    fullText={this.handleFullText} 
                    onFullTextEdit={this.handleFullTextEdit}
                />
            </WprSekcja>
        );
    }

    calosc() {
        return (
            <div className="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
            
                {this.P(1)}
                {this.P(2)}
                {this.P(3)}
                {this.P(4)}
                {this.P(5)}
                {this.P(6)}
                {this.P(7)}

                <WprSekcja num="8" 
                    title="Informacja uszczegóławiająca"
                    readOnly={this.state.readonly}
                >
                    <div className="wstep">
                        Informacja uszczegóławiająca, wynikająca z potrzeb lub specyfiki jednostki
                    </div>
                    <Wprowadz8 
                        len={this.state.p8.length} 
                        form={this.state} 
                        onP8Change={this.handleP8Change} 
                        onDodaj={this.handleDodaj} 
                        onP8Show={this.handleP8Show}
                        onP8Edit={this.handleP8Edit}
                    />
                </WprSekcja>

            </div>            
        );
    }
}

export default Wprowadz;