import React, { Component } from 'react';
import { Tekst, Input } from '../forms';

class Wprowadz1 extends Component {

    componentDidMount() {
        if (this.foc && !this.props.form.readonly)
            this.foc.focus();
    }

    handleFocusRef(input) {
        this.foc= input;
    }

    render() {
        return (
            <div>
                <Tekst nazwa="p1_nazwa_firmy" 
                    etykieta="Nazwa firmy" 
                    pomoc="Pełna nazwa firmy" 
                    rows="2" 
                    focusRef={this.handleFocusRef}
                    {...this.props}
                />

                <div className="row">
                    <Input nazwa="p1_wojewodztwo" etykieta="Województwo" {...this.props}/>
                    <Input nazwa="p1_powiat" etykieta="Powiat" {...this.props}/>
                    <Input nazwa="p1_gmina" etykieta="Gmina" {...this.props}/>
                </div>
                
                <div className="row">
                    <Input nazwa="p1_miejscowosc" etykieta="Miejscowość" {...this.props}/>
                    <Input nazwa="p1_kod_pocztowy" etykieta="Kod pocztowy" {...this.props}/>
                    <Input nazwa="p1_poczta" etykieta="Poczta" {...this.props}/>
                </div>

                <div className="row">
                    <Input nazwa="p1_ulica" etykieta="Ulica" {...this.props}/>
                    <Input nazwa="p1_nr_domu" etykieta="Nr domu" {...this.props}/>
                    <Input nazwa="p1_nr_lokalu" etykieta="Nr lokalu" {...this.props}/>
                </div>

                <Tekst nazwa="p1_pkd" etykieta="Przedmiot działalności jednostki" pomoc="Kody PKD określające podstawową działalność podmiotu" rows="1" {...this.props}/>

                <div className="row">
                    <div className="col-md-12 wstep">
                        Identyfikator podmiotu składającego sprawozdanie finansowe we właściwym rejestrze sądowym albo ewidencji.
                        W przypadku sprawozdań finansowych składanych do Szefa KAS wypełnia się identyfikator podatkowy.
                        W sprawozdaniach finansowych składanych do KRS wypełnia się numer KRS.
                    </div>
                    <Input nazwa="p1_nip" etykieta="Identyfikator podatkowy (NIP)" {...this.props}/>
                    <Input nazwa="p1_krs" etykieta="Numer KRS" {...this.props}/>
                </div>

            </div>
        );
    }
}

export default Wprowadz1;