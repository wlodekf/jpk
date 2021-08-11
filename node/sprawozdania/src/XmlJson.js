import React, { Component } from 'react';
import api from './utils/api';

var convert = require('xml-js');

var xml,_xml, _json;

async function loadXml() {
    xml = await api.xml_get();
    xml= xml.data;
    //console.log(xml);
    
    _json = convert.xml2json(xml, {compact: true, spaces: 4});
    
    console.log(_json);
    /*

    _xml = convert.json2xml(_json, {compact: true, ignoreComment: false, spaces: 4});

    console.log(_xml);
*/
    return _json;
}

export default loadXml;
