import React from 'react';
import ReactDOM from 'react-dom';

import './index.css';

import Raport from './components/raport/Raport';
import Wprowadz from './components/wprowadzenie/Wprowadz';
import Podatek from './components/podatek/Podatek';
import Dodatkowe from './components/dodatkowe/Dodatkowe';

//import * as serviceWorker from './serviceWorker';

if (window.location.href.indexOf('wprowadz') >= 0)
    ReactDOM.render(<Wprowadz ref={(app) => {window.app = app}}/>, document.getElementById('wprowadz'));
else if (window.location.href.indexOf('podatek') >= 0)
    ReactDOM.render(<Podatek ref={(app) => {window.app = app}}/>, document.getElementById('podatek'));
else if (window.location.href.indexOf('dodatkowe') >= 0)
    ReactDOM.render(<Dodatkowe ref={(app) => {window.app = app}}/>, document.getElementById('dodatkowe'));
else
    ReactDOM.render(<Raport ref={(app) => {window.app = app}}/>, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
//serviceWorker.unregister();
