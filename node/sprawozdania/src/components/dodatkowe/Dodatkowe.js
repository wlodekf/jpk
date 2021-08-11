import React, { Component } from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import { Zalacznik } from './Zalacznik';
import Lista from './Lista';

export default class Dodatkowe extends Component {
    render() {
        return (
            <BrowserRouter basename={window.location.pathname}>
                <div className="panel-body">
                    <form onChange={this.handleChange} autoComplete="off">
                        <Switch>
                            <Route exact path="/" component={Lista} />
                            <Route path="/:id/" component={Zalacznik} />
                        </Switch>
                    </form>
                </div>
            </BrowserRouter>
        );
    }
}
