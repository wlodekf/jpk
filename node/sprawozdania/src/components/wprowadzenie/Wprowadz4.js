import React, { Component } from 'react';
import { Wskazanie } from '../forms';

// Wskazanie czy sprawozdanie zawiera dane łączne

class Wprowadz4 extends Component {

    render() {
        return (
            <div>
                <Wskazanie nazwa="p4_laczne" 
                    etykieta="Sprawozdanie finansowe zawiera dane łączne" 
                    {...this.props} />
            </div>
        );
    }
}

export default Wprowadz4;