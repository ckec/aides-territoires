import React from "react";
import { Link } from "react-router-dom";
import "./navigation.css";

class Navigation extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      mobileMenuIsActive: false
    };
  }
  handleClick = () => {
    this.setState({
      mobileMenuIsActive: !this.state.mobileMenuIsActive
    });
  };
  handleLinkClick = () => {
    this.setState({
      mobileMenuIsActive: false
    });
  };
  render() {
    return (
      <nav className="navbar navigation" aria-label="main navigation">
        <div className="navbar-brand">
          <Link className="navbar-item" to="/">
            <img
              alt="logo gouv"
              style={{ paddingRight: "20px" }}
              src="/images/logo-gouv.png "
            />{" "}
            <img
              alt="logo aides-territoires"
              style={{ paddingRight: "20px" }}
              src="/images/logo-aides-territoires.png "
            />
            <p className="app-name ">
              <strong>Aides-territoires</strong>
            </p>
          </Link>
          <div
            className={
              this.state.mobileMenuIsActive
                ? "navbar-burger is-active"
                : "navbar-burger"
            }
            data-target="navMenu"
            onClick={this.handleClick}
          >
            <span />
            <span />
            <span />
          </div>
        </div>
        <div
          className={
            this.state.mobileMenuIsActive
              ? "navbar-menu is-active"
              : "navbar-menu"
          }
          id="navMenu "
        >
          <div className="navbar-end">
            <Link className="navbar-item" to="/">
              Accueil
            </Link>
            <Link className="navbar-item" to="/" onClick={this.handleLinkClick}>
              Contact
            </Link>
          </div>
        </div>
      </nav>
    );
  }
}

export default Navigation;