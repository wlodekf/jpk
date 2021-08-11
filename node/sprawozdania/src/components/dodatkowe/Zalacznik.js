import React, { Component } from 'react';
import { Tekst } from '../forms';
import api from '../../utils/api';

export class Zalacznik extends Component {

    constructor(props) {
        super(props);

        this.state= {}

        for(const f of Object.getOwnPropertyNames(Object.getPrototypeOf(this))) {
            if (f.startsWith('handle') || f.startsWith('toggle')) 
                this[f]= this[f].bind(this);
        }
    }
    
    // Wczytanie danych załącznika
    async componentDidMount() {
        let pozycja= {id: 0, opis: '', nazwa: ''};

        if (this.props.match.params.id !== "0") {
            const result= await api.zalacznik_get();
            pozycja= result.data;
        }

        this.setState(pozycja);
    }

    // Zapamiętanie wybranego pliku
    handleFileChange(e) {
        this.setState({
            selectedFile: e.target.files[0],
            nazwa: e.target.files[0].name
        });
    }

    // Zmiana opisu załącznika
    handleOpisChange(e) {
        this.setState({ opis: e.target.value, tah: e.target.scrollHeight});
    }

    // To w komponencie załącznika
    async handleSave(e) {
        e.preventDefault();

        const data = new FormData();

        const plik= this.state.selectedFile;
        const nazwa= plik? plik.name : undefined;
        data.append('file', plik, nazwa);

        const { id, opis } = this.state;
        const form= { id, opis };
        data.append('form', JSON.stringify(form));
    
        const res= await api.zalacznik_save(id, data);

        this.setState({...res.data.poz});
        this.handleToList();
    }

    // Usunięcie załącznika przy pomocy api i przekierowanie na listę
    async handleDelete(e) {
        e.preventDefault();

        await api.zalacznik_del();

        this.handleToList();
    }

    handleToList() {
        this.props.history.push('/');
    }

    render() {
        const form= {readonly: false};

        return (
            <div className="panel panel-default">
                <div className="panel-body">

                    <div className="form-group">
                        <label htmlFor="nazwa_pliku" className="control-label">Plik załącznika</label>
                        <div className="input-group">
                            <label className="input-group-btn">
                                <span className="btn btn-primary">
                                    Wybór pliku <input type="file" onChange={this.handleFileChange} />
                                </span>
                            </label>
                            <input type="text" id="nazwa_pliku" value={this.state.nazwa} className="form-control" readOnly/>
                        </div>
                    </div>

                    <Tekst nazwa="opis" 
                            rows="5" 
                            etykieta="Opis zawartości załącznika" 
                            value={this.state.opis} 
                            form={form} 
                            onChange={this.handleOpisChange}
                    />

                    <div className="przyciski przyciski2">
                        <button className="btn btn-default" type="submit" value="Save" onClick={this.handleSave}>Zapisz</button>
                        <button className="btn btn-default" type="submit" value="Delete" onClick={this.handleDelete}>Usuń</button>            
                        <button className="btn btn-default cancel" value="Cancel" onClick={this.handleToList}>Rezygnuj ze zmian</button>
                    </div>

                </div>
            </div>
        );
    }
};
