import { poll_status, timer_add } from './timer';
import { rozwin } from './rows';

const TABLES= {
    'jpk': ['table', jpk_data_table],
    'firmy': ['firmy', firmy_data_table],
    'fakturyl': ['faktury', faktury_data_table]
}

export function init_data_table() {
    for (let tableid in TABLES)
        if ($('#'+tableid).length) {
            const tab= TABLES[tableid];
            window[tab[0]]= tab[1]();
        }
}

/**
 * Po załadowaniu tabeli plików JPK rozwinięcie ostatnio
 * oglądanego wiersza.
 */
function rozwiniecie() {
    if (tr_id)
        rozwin($("tr#tr_"+tr_id)[0], tr_id);	
}

/**
 * Inicjalizacja tabeli plików JPK
 */
function jpk_data_table() {

    return $('#jpk').on('init.dt', function() {
            poll_status();
            rozwiniecie();
        }).DataTable({

        "language": {
            "url": "/static/DataTables/Polish.json"
        },

        ajax: "/ajax"+window.location.pathname+"jpk/lista/",   

        columns: [
            { data: 'numer' },
            { data: 'utworzony' },
            { data: 'kod' },
            { data: 'dataod' },
            { data: 'datado' },
            { data: 'opis' },
            { data: 'stan' }
        ],  
        columnDefs: [
            { "width": "25%", "targets": 5 }
        ],	
        info: false,
        stateSave: true,
        lengthMenu: [10, 15, 20, 100],
        pageLength: 15,
        createdRow: function ( row, data, index )
        {
            if(data.stan == 'W KOLEJCE' || data.stan == 'TWORZENIE')
                timer_add(index, data.numer, data.czas);
            $(row).attr('id', 'tr_'+data.numer);
            if(data.stan == 'DOSTARCZONY')
                $('td', row).eq(6).addClass('hl_green');
            if(data.stan == 'NIE WYSŁANY' || data.stan == 'NIE PRZYJĘTY' || data.stan == 'BŁĄD WYSYŁKI')
                $('td', row).eq(6).addClass('hl_red'); 
            console.log(data.numer, data.bledy);
            if(data.bledy == 'error') 
                $('td', row).eq(6).addClass('hl_bledy');
            if(data.bledy == 'warn') 
                $('td', row).eq(6).addClass('hl_warn');   
        },
        order: [[ 0, 'desc' ]]    
    });
}

// Inicjalizacja tabeli firm
function firmy_data_table() {

    return $('#firmy').DataTable({
        "language": {
            "url": "/static/DataTables/Polish.json"
        },

        ajax: "/ajax/firmy/",   

        columns: [
            { data: 'oznaczenie' },
            { data: 'nazwa' },
            { data: 'kod' },
            { data: 'okres' },
            { data: 'opis' },
            { data: 'stan' },
        ],  

        columnDefs: [
            { "width": "5%", "targets": 0 }
        ],
            
        info: false,
        stateSave: true,
        lengthMenu: [10, 15, 20, 100],	
        pageLength: 20,
        order: [[ 0, 'asc' ]]    
    });
}

// Inicjalizacja tabeli faktur
function faktury_data_table() {

    return $('#fakturyl').DataTable({

        "language": {
            "url": "/static/DataTables/Polish.json"
        },

        ajax: "/bra/ajax/faktury/",   

        columns: [
            { data: 'faktura' },
            { data: 'daty' },
            { data: 'nip' },
            { data: 'nazwa' },
            { data: 'adres' },
            
            { data: 'sprzedaz23' },
            { data: 'sprzedaz8' },
            { data: 'sprzedaz5' },
            { data: 'sprzedaz0zw' },
            { data: 'naleznosc' },
            
            { data: 'rodzaj' }
        ],  

        columnDefs: [
            { "width": "40px", "targets": 1 },    
            { "width": "20%", "targets": [3, 4] },
            { "sClass": "ar", "targets": [ 5, 6, 7, 8, 9 ] }               
        ],
            
        info: false,
        stateSave: true,
        lengthMenu: [10, 15, 20, 100],
        pageLength: 10,
        
        order: [[ 0, 'asc' ]]    
    });
}