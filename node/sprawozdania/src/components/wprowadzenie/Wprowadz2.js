import React, { Component } from 'react';
import { Tekst, Data } from '../forms';

class Wprowadz2 extends Component {

    render() {
        const p=  this.props;
        return (
            <div>
                <div className="row">
                    <Data nazwa="p2_data_od" etykieta="Od dnia" {...p}/>
                    <Data nazwa="p2_data_do" etykieta="Do dnia" {...p}/>
                </div>

                <Tekst nazwa="p2_data_do_opis" 
                    etykieta="Do kiedy" 
                    rows="2" {...p} 
                    pomoc='Opis terminu zakończenia działalności (alternatywny do "Do dnia")'/>
            </div>
        );
    }
}

export default Wprowadz2;