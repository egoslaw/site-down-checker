import React from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';

const SiteTable = ({ sites }) => {
  console.log(sites);
  const siteList = sites.length
    ? sites.map(function(site, index) {
        return (
          <tr key={site.id}>
            <td>{index + 1}</td>
            <td><Link to={`/site/${site.id}`}>{site.url}</Link></td>
            <td>{site.last_status ? site.last_status : 'None'}</td>
            <td>{site.last_response_time ? site.last_response_time : 'None'}</td>
            <td>{site.last_check.slice(0, 16).replace("T", " ")}</td>
          </tr>
        );
      })
    : null;
  if (siteList) {
    return (
      <div className="containter">
        <div className="center">
          <table className="striped bordered">
            <thead>
              <tr>
                <th>Id</th>
                <th>Url</th>
                <th>Last status</th>
                <th>Last response time</th>
                <th>Last checked</th>
              </tr>
            </thead>
            <tbody>{siteList}</tbody>
          </table>
        </div>
      </div>
    );
  } else {
    return (
      <div className="center">
        <p>No data</p>
      </div>
    );
  }
};


const mapStateToProps = (state) => {
  return {
    token: state.token,
    sites: state.sites
  }
}

export default connect(mapStateToProps)(SiteTable);
