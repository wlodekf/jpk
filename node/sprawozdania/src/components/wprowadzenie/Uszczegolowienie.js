import React from 'react';
import { Tekst, Input } from '../forms';
import { formatText } from '../../utils/utils';

export default function Uszczegolowienie(props) {
    if (!props.form.readonly || props.form.p8_lp < 0)
        return (
            <UszczegolowienieEdit {...props}/>
        );
    else
        return (
            <div>
                <h4 className="list-group-item-heading nag">{props.form.p8_nazwa}</h4>

                {formatText(props.form.p8_opis)}

                <button className="btn btn-default" onClick={props.onP8Edit}>Zmień</button>
                <button className="btn btn-default cancel" onClick={props.onP8Usun}>Usuń uszczegółowienie</button>
                <button className="btn btn-default" onClick={props.onP8Back}>Powrót do wprowadzenia</button>
            </div>
        );

};

const UszczegolowienieEdit= (props) => {
    const {form, onP8Save, onP8Anuluj}= props;

    return (
        <div>
            <div className="wstep">
                Informacja uszczegóławiająca, wynikająca z potrzeb lub specyfiki jednostki
            </div>

            <div className="row">
                <Input nazwa="p8_nazwa" cols="12" etykieta="Nazwa pozycji" value={form.p8_nazwa} {...props}/>
            </div>

            <Tekst nazwa="p8_opis" rows="10" etykieta="Opis" value={form.p8_opis} {...props}/>

            <button className="btn btn-default" type="submit" value="Zapisz" onClick={onP8Save}>Zapisz</button>
            <button className="btn btn-default cancel" value="Anuluj" onClick={onP8Anuluj}>Rezygnuj ze zmian</button>
        </div>
    );
};
