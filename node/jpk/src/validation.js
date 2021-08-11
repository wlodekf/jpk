// Sprawdzenie popdatności daty
const poprawna_data= function (data) {

	var IsoDateRe= new RegExp("^([0-9]{4})-([0-9]{2})-([0-9]{2})$");
    var matches= IsoDateRe.exec(data);
      
  	if (!matches) return false;

  	var composedDate= new Date(matches[1], (matches[2]-1), matches[3]);
  	return (composedDate.getMonth() == (matches[2]-1)) && 
  		   (composedDate.getDate() == matches[3]) && 
  		   (composedDate.getFullYear() == matches[1]);
}

// Sprawdzenie poprawności danych formularza tworzenia pliku JPK
export default function poprawne_dane()
{
	var dataod= $('#dataod').val();
	if(dataod==null || dataod=="") {
		alert('Podaj datę początku okresu JPK');
		return false;
	}
	if(!poprawna_data(dataod)) {
		alert('Niepoprawna data początku okresu: '+dataod);
		return false;
	}
	
	var datado= $('#datado').val();
	if(datado==null || datado=="") {
		alert('Podaj datę końca okresu JPK');
		return false;
	}	
	if(!poprawna_data(datado)) {
		alert('Niepoprawna data: '+datado);
		return false;
	}
	
	return true;
}
