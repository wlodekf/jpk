import React, { Component } from 'react';

// Sekcja wprowadzenia do sprawozdania

class WprSekcja extends Component {

    constructor(props) {
        super(props);

        this.edytuj= this.edytuj.bind(this);
    }

    edytuj(e) {
        return this.props.onSectionEdit(e, this.props.num);
    }

    ikony() {
        if (this.props.readOnly)
            return (
                <ul className="nav navbar-nav przyciski">
                    {this.props.num > 0 && this.props.num < 7 &&
                    <li onClick={this.edytuj}>
                        <span className="glyphicon glyphicon-pencil" aria-hidden="true"></span>
                    </li>
                    }
                </ul>
            );

        return (
            <ul className="nav navbar-nav przyciski">
                <li onClick={this.props.onZapisz}>
                    <span className="glyphicon glyphicon-floppy-disk" aria-hidden="true"></span>
                </li>
                <li onClick={this.props.onCancelEdit}>
                    <span className="glyphicon glyphicon-remove" aria-hidden="true"></span>
                </li>
            </ul>
        );
    }

    render() {
        const { num, title } = this.props;
        this.initClass= (this.props.num === '1')?'in':'';

        return (
            <div className="panel panel-default">
                <div className="panel-heading" _role="tab" id={`heading${num}`}>
                    {this.ikony()}

                    <h4 className="panel-title naglowek">
                        <a role="button" data-toggle="collapse" data-parent="#accordion" href={`#collapse${num}`} aria-expanded="true" aria-controls={`collapse${num}`}>
                            {num}. {title}
                        </a>
                    </h4>
                </div>

                <div className="panel-body">
                    {this.props.children}

                    {this.props.readOnly ||
                        <div className="row przyciski">
                            <button className="btn btn-success" onClick={this.props.onZapisz}>Zapisz</button>
                            <button className="btn btn-warning cancel" onClick={this.props.onCancelEdit}>Rezygnuj ze zmian</button>
                        </div>
                    }
                </div>
            </div>
        );
    }
}

export default WprSekcja;
