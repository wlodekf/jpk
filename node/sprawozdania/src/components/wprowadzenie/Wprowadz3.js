import React, { Component } from 'react';
import { Input, Data } from '../forms';

// Okres sprawozdania i data sporządzenia

class Wprowadz3 extends Component {

    render() {
        return (
            <div>
                <div className="row">
                    <Data nazwa="p3_data_od" etykieta="Początek okresu" {...this.props}/>
                    <Data nazwa="p3_data_do" etykieta="Koniec okresu" {...this.props}/>
                </div>
                
                <div className="row">
                    <Input nazwa="p0_data_sporzadzenia" 
                        etykieta="Sporządzone" 
                        pomoc="Data sporządzenia sprawozdania" 
                        {...this.props}/>
                </div>
            </div>
        );
    }
}

export default Wprowadz3;
