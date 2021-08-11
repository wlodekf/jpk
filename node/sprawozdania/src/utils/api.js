import axios from 'axios';

const FORM_HEADERS= { 
    headers: { 'Content-Type': 'multipart/form-data' } 
};

const ACCEPT_JSON= { 
    headers: { 'Accept': 'application/json' } 
};

const url= (path) => window.location.href.replace('jpk/', 'sf/').replace('#', '') + (path?path+'/':'');

const p8_save= (poz) => {
    // Zapisanie nowego dodatkowego wyjaśnienia lub modyfikacja
    let data = new FormData();
    let d= JSON.stringify(poz);
    data.append('data', d);

    const response= poz.p8_id?axios.patch(url('p8/'+poz.p8_id), data) : axios.post(url('p8'), data);

    response.then(response => {
        data= response.data;
        poz.p8_id= data.p8_id;
    })
        .catch(errors => console.log(errors)); 
};

const wprowadz_get= () => axios.get(url(''), ACCEPT_JSON);
const wprowadz_save= (data) => axios.patch(url(''), data, FORM_HEADERS);
const p8_del= ([poz8]) => axios.delete(url('p8/'+poz8.p8_id));

const raport_get= () => axios.get(url(''), ACCEPT_JSON);
const raport_save= (data) => axios.patch(url(''), data); // JSON default

const podatek_get= () => axios.get(url(''), ACCEPT_JSON);
const podatek_save= (data) => axios.patch(url(''), data, FORM_HEADERS);

const zalacznik_get= () => axios.get(url(''), ACCEPT_JSON);
const zalacznik_url= (poz_id) => url(poz_id+'/plik');
const zalacznik_save= (id, data) => id? axios.patch(url(''), data, FORM_HEADERS) : axios.post(url(''), data, FORM_HEADERS);
const zalacznik_del= () => axios.delete(url(''));

const xml_get= () => axios.get('/jpk/1172/download/');

const api= {
    wprowadz_get, wprowadz_save,
    p8_del, p8_save, 
    raport_get, raport_save,
    podatek_get, podatek_save,
    zalacznik_get, zalacznik_save, zalacznik_del, zalacznik_url,
    xml_get
};

export default api;
