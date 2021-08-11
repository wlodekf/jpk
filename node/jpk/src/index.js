/**
 * Obsługa plików JPK
 */

import { init_data_table } from './tables';
import { show_details, refresh_row, rozwin } from './rows';
import poprawne_dane from './validation';
import './jpk.css';

$(function() {

    init_data_table();

    $('#jpk tbody').on('click', 'tr[role="row"]', function () {
        rozwin(this);
    });

    $('#firmy tbody').on('click', 'tr[role="row"]', function () {
        const tr = $(this).closest('tr');
        const row = firmy.row( tr );
        const d= row.data();
        window.location.href = "/"+d.oznaczenie+'/';
    } );
    
    $("#jpk_wb").click(function() {
        $("#rachunki").toggle();
    }); 

    $("#jpk_mag").click(function() {
        $("#magazyny").toggle();
    });

    $("#przeplywy").click(function() {
        $("#metoda_przeplywow").toggle();
    });

    $("#jpk_sf").click(function() {
        $("#sprawozdanie").toggle();
        if($('#sprawozdanie').is(':visible')) {
            const rok= new Date().getFullYear()-1;
            const poczatek= new Date(rok+'-01-01');
            const koniec= new Date(rok+'-12-31');
            $('#dataod').val(poczatek.toISOString().substring(0,10));
            $('#datado').val(koniec.toISOString().substring(0,10));
        }
    });

    $(".naglowek-paczki").first().next().toggle();

    $("span.tog").click(function() {
        $(this).parent().next().toggle();
    }); 

    $(document).on("click", ".dodaj-paczke", function () {
        const paczkaId = $(this).data('paczka');
        $(".modal-body #paczka").val( paczkaId );
        $('#plik-modal').modal('show');     
    });

    $(document).on("click", ".jpk-przygotuj", function () 
    {
        $('#initupload-modal').modal('hide');  
        const jpk_id= $(this).parent().find('#initupload_jpk_id').val();
        const row= table.row($('#tr_'+jpk_id));
        
        setTimeout(function() { 
            refresh_row(row);
            show_details(row); 
        }, 2000);
    });

    $(document).on("click", ".plik-upload", function () 
    {
        const jpk_id = $(this).data('jpk_id');
        $("#jpk_id").val( jpk_id );
        $('#upload-modal').modal('show');     
    });

    $(document).on("click", ".sf-upload", function () 
    {
        const jpk_id = $(this).data('jpk_id');
        $("#sf-jpk_id").val( jpk_id );
        $('#sf-modal').modal('show');     
    });

    $(document).on("click", ".plik-initupload", function () 
    {
        const jpk_id = $(this).data('jpk_id');
        $("#initupload_jpk_id").val( jpk_id );
        $('#initupload-modal').modal('show');     
    });

    $(document).on("click", ".jpk-nazwa", function () 
    {
        $("#nazwa-jpk_id").val($(this).data('jpk_id'));
        $("#id_nazwa").val($(this).data('nazwa'));
        $('#nazwa-modal').modal('show');
    });

    $('.modal').on('shown.bs.modal', function () {
        $(this).find('input:text:visible:first').focus();
    });

    $("#pliki-form").submit(function( event ) {
        if(!poprawne_dane()) {
            event.preventDefault();
        }
    });

    $(document).on("click", "li.disabled", function(event) {
        event.preventDefault();
        return false;
    });

    function alertSetup() {
        $(".alert").slideDown('slow', function() {
            // Timeout to hide the message, can be set in alert element 
            // with data-timeout attribute
            const timeout= $(this).data('timeout') || 2000;
            setTimeout(() => {
                // After 'timeout' millis message is removed
                $(this).slideUp('slow', () => $(this).remove());
            }, timeout);
        });
        
        $(".alert").click(function() {
            $(this).slideUp('slow', () => $(this).remove());
        });
    }

    alertSetup();

    $('#initupload-form').on('submit', function() {
        if($('#id_plik').get(0).files.length === 0)
            return false;
    });

    $("#oznaczenie").change(function() {
        $.getJSON("/ajax/"+$("#oznaczenie").val()+"/dane/", function(data) {
            $('#nazwa').val(data.nazwa);
            $('#nip').val(data.nip);		
        });
    });

    $(document).on("click", "input.cancel", function () {
        window.location.href= $(this).data("url");
    });

    $("#konto_kon").change(function() {
        if($("#konto_kon").val()) {
            $.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_kon").val()+"/", function(data) {
            if(data.errors) 
                $("#konto_spr-div").addClass("has-error");	
            else
                $("#konto_spr-div").removeClass("has-error");		
            $("#konto_kon-help").html(data.nazwa);
            });
        }
        else
            $("#konto_kon-help").html('');	
    });

    $("#konto_spr").change(function() {
        $.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_spr").val()+"/", function(data) {
            if(data.errors) 
                $("#konto_spr-div").addClass("has-error");	
            else
                $("#konto_spr-div").removeClass("has-error");						
            $("#konto_spr-help").html(data.nazwa);
        });
    });

    $(window).on("beforeunload", function(e) {
        if (window.app && window.app.zapisane && !window.app.zapisane())
            return "Dane nie zostały zapisane";
    });


    window.jpk_log= function(message, level, timeout) {
        $('.main-container').prepend(
            `<div class="alert alert-${level}" role="alert" data-timeout="${timeout}">${message}</div>`
        );
        alertSetup();	
    };

    window.jpk_error= function(message, error) {
        jpk_log(`${message}: ${error}`, 'danger', 4000);
    }

    window.jpk_info= function(message) {
        jpk_log(message, 'success', 2000);
    }
});
