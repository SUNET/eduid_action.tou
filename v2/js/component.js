
import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { connect } from 'react-redux';

class Main extends Component {

    render () {

        return (
            <div className="container-fluid">
            hello world!
            </div>
        );
    }
}

Main.propTypes = {
}

const mapStateToProps = (state, props) => {
    return {
    }
};

const mapDispatchToProps = (dispatch, props) => {
    return {
    }
};

const MainContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Main);

export default MainContainer;

