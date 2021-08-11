import React, { Component } from 'react';
import { skrotTekstu } from '../../utils/utils';
import api from '../../utils/api';
import { Link } from 'react-router-dom';

export default class ZalacznikSkrot extends Component {

    ikony() {
        return (
            <ul className="nav navbar-nav przyciski">
                <li>
                    <Link to={`/${this.props.poz.id}/`} className="link-ikona">
                        <span className="glyphicon glyphicon-pencil" aria-hidden="true"></span>
                    </Link>
                </li>
            </ul>
        );
    }

    render() {
        const { poz } = this.props;

        return (
            <div className="panel panel-default">
                <div className="panel-heading">
                    {this.ikony()}
                    <a href={api.zalacznik_url(poz.id)}>{poz.nazwa}</a>
                </div>

                <div className="panel-body">
                    {skrotTekstu(poz.opis)}
                </div>
            </div>
        );
    }
}