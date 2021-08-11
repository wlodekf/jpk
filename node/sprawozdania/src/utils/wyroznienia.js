const WYROZNIENIA= {
    Aktywa: {
        1: 'UB',
        2: 'UBS',
        3: 'B'
    },
    Pasywa: {
        1: 'UB',
        2: 'UBS',
        3: 'B'
    },

    RZiSKalk: {
        1: 'UBS'
    },

    RZiSPor: {
        1: 'UBS'
    },

    ZestZmianWKapitale: {
        1: 'UBS',
        2: 'B'
    },

    PrzeplywyBezp: {
        1: 'UBS',
        2: 'B'
    },

    PrzeplywyPosr: {
        1: 'UBS',
        2: 'U'
    },
};

export const wyroznienie= (rapel, w) => {
    const wyr= WYROZNIENIA[rapel];
    return wyr[w.klu1.length] ? `wyr${wyr[w.klu1.length]}` : '';
};

export const wyr_podatek= (w, podstawa) => {
    const wyr= {1: podstawa?'UBS kontener':''};
    return wyr[w.klucz.length] ? `wyr${wyr[w.klucz.length]}` : '';
};
