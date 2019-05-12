import React, { Component } from "react";
import axios from "axios";
import SiteTable from '../SitesTable/SitesTable';
import NewUrl from '../NewUrl/NewUrl';
import AuthenticateCheck from '../../hoc/AuthenticateCheck';
import { connect } from 'react-redux';
import { updateSites } from '../../actions/siteActions';
import { updateToken } from '../../actions/authenticateActions';
import ProxyChangeToggle  from '../ProxyChangeToggle/ProxyChangeToggle';

class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {
      sites: this.props.sites,
    }
  }
  componentDidMount() {
    if (!this.props.sites.length) {
      axios.get("http://127.0.0.1:8000/api/sites/", {
        headers: {
          Authorization: `Token ${localStorage.getItem('token')}`
        }
      }).then(res => {
        this.props.updateSites(res.data)
      });
    } else {
    }
  }

  refreshSite = (id, index) => {
    const url = `http://127.0.0.1:8000/api/sites/${id}/`
    axios.put(url, {},{
      headers: { 'Authorization': `Token ${this.props.token}` }
    })
      .then(response => {
        let data = response.data
        this.props.refreshSite(id, index, data)
      })
      .catch(error => {    
      });
  }

  handleLogout = () => {
    localStorage.clear()
    alert('You were logged out')
    this.props.updateToken()
  }

  render() {
    return (
      <div className="container">
        <p>You are logged as {localStorage.getItem('username')}</p>
        <button type="submit" onClick={this.handleLogout}>Logout</button>
        <SiteTable sites={this.props.sites} /><br/>
        <NewUrl sites={this.props.sites}/>
        <ProxyChangeToggle />
      </div>
    );
  }
}
const mapStateToProps = (state) => {
  return {
    token: state.token,
    sites: state.sites
  }
}

const mapDispatchToProps = {
  updateSites,
  updateToken,
}

export default connect(mapStateToProps, mapDispatchToProps)(AuthenticateCheck(Home));