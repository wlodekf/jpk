import React, { Component } from 'react';
import api from '../../utils/api';
import ZalacznikSkrot from './Skrot';

export default class Lista extends Component {

    constructor(props) {
        super(props);

        this.state= {pozycje: []};
        this.handleDodaj= this.handleDodaj.bind(this);
    }

    async componentDidMount() {
        const result= await api.zalacznik_get();
        this.setState({ pozycje: result.data.pozycje });
    }

    handleDodaj(e) {
        e.preventDefault();
        this.props.history.push('/0/');
    }

    render() {
        return (
            <div className="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
                <div className="list-group">
                    {this.state.pozycje.map((poz, lp) => 
                        <ZalacznikSkrot key={poz.id} poz={poz} />
                    )}
                </div>

                <button className="btn btn-default" onClick={this.handleDodaj}>Dodaj załącznik</button>
            </div>
        );   
    }
}
