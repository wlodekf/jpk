import React from 'react';

function podzial_na_linie(txt) {
    return txt.split('\n').map((a, lp) =>
        <React.Fragment key={lp}>
            {a}<br/>
        </React.Fragment>
    );
}

export function formatText(txt) {
    return txt.split('\n\n').map((a, lp) => 
        <p key={lp}>{podzial_na_linie(a)}</p>
    );
}

export function skrotTekstu(txt) {
    if (!txt) return null;

    const linie= txt.split('\n\n');
    if (linie.length > 2) {
        return (
            <React.Fragment>
                <p>{linie[0]}</p>
                <p>{linie[1]}</p>
                ...
            </React.Fragment>
        );
    }

    return (
        <React.Fragment>
            {linie.map((linia, lp) => <p key={lp}>{linia}</p>)}
        </React.Fragment>
    );
}