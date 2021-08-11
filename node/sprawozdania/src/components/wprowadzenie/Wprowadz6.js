import React, { Component } from 'react';
import { Wskazanie, Tekst } from '../forms';

// Sprawozdanie po połączeniu spółek

class Wprowadz6 extends Component {

    render() {
        return (
            <div>
                <Wskazanie nazwa="p6_po_polaczeniu" {...this.props} etykieta="Sprawozdanie finansowe sporządzone po połączeniu spółek"/>
                <Tekst nazwa="p6_metoda" {...this.props} etykieta="Zastosowana metoda rozliczenia połączenia (nabycia, łączenia udziałów)"/>
            </div>
        );
    }
}

export default Wprowadz6;
