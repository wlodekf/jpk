import React, { Component } from 'react';
import UszczegolowienieSkrot from './UszczegolowienieSkrot';

// Uszczegółowienia

class Wprowadz8 extends Component {

    uszczegolowienia() {
        if (!this.props.form || !this.props.form.p8)
            return '';

        return this.props.form.p8.map((poz, lp) => 
            <UszczegolowienieSkrot key={lp} len={this.props.len} lp={lp} poz={poz} {...this.props}/>
        );
    }

    render() {
        return (
            <React.Fragment>
                <div className="list-group">
                    {this.uszczegolowienia()}
                </div>
                <button className="btn btn-default" onClick={this.props.onDodaj}>Dodaj uszczegółowienie</button>
            </React.Fragment>
        );
    }
}

export default Wprowadz8;
