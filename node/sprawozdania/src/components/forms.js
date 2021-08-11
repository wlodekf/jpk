import React, { Component } from 'react';

export class Tekst extends Component {

    componentDidMount() {
        this.props.onMount && this.props.onMount(this.props.nazwa);
    }

    render() {
        const {nazwa, etykieta, pomoc, rows, form={}, value, onChange= ()=>{}} = this.props;

        let height= {};
        if ((nazwa.startsWith('p7_') || (nazwa==='p8_opis')) && !form.readonly && form.tah)
            height= {height: form.tah};

        return (
            <div className="row">
                <div className="col-md-12">
                    <div className="form-group">
                        {(nazwa.indexOf('p7_')<0) && <label className="control-label">{etykieta}</label>}
                        
                        <textarea 
                            readOnly={form.readonly} 
                            className={`form-control ${form.readonly || 'edycja'}`}
                            rows={rows} 
                            id={nazwa} 
                            name={nazwa} 
                            value={value||form[nazwa]} 
                            onChange={onChange} 
                            ria-describedby={nazwa+'-help'}
                            style={height}
                            ref={(input) => this.props.focusRef && this.props.focusRef(input)}
                        ></textarea>

                        {pomoc?<p id={nazwa+'-help'} className="help-block">{pomoc}</p>:''}
                    </div> 
                </div>
            </div>
        );
    }
}

export const Input= ({nazwa, etykieta, pomoc, cols=4, form={}, value, onChange= ()=>{}}) =>(
    <div className={'col-md-'+cols}>
        <div className="form-group">
            <label className="control-label">{etykieta}</label>
            <input readOnly={form.readonly} type="text" className="form-control" id={nazwa} name={nazwa} value={value||form[nazwa]} onChange={onChange} aria-describedby={nazwa+'-help'}/>
            {pomoc?<p id={nazwa+'-help'} className="help-block">{pomoc}</p>:''}
        </div> 
    </div>);

export const Data= ({nazwa, etykieta, cols=4, form={}, value, onChange= ()=>{}}) => (
    <div className={'col-md-'+cols}>
        <div className="form-group">
            <label className="control-label">{etykieta}</label>
            <input readOnly={form.readonly} type="text" pattern='\d{4}-\d{2}-\d{2}' className="form-control" id={nazwa} name={nazwa} value={value||form[nazwa]} onChange={onChange} aria-describedby={nazwa+'-help'}/>
            <p id={nazwa+'-help'} className="help-block">Data w formacie RRRR-MM-DD</p>
        </div> 
    </div>);

export const Wskazanie= ({nazwa, etykieta, cols=12, form={}, value}) =>(
    <div className="row">
        <div className={'col-md-'+cols}>
            <div className="checkbox">
                <label>
                    <input type="checkbox" id={nazwa} name={nazwa} checked={value||form[nazwa]}/> {etykieta}
                </label>
            </div>
        </div>
    </div>);