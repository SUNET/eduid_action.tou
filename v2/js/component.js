
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import ActionWrapperContainer from "containers/ActionWrapper";

class Main extends Component {

    render () {

        return (
            <ActionWrapperContainer>
            hello world!
            </ActionWrapperContainer>
        );
    }
}

Main.propTypes = {
}

const MainContainer = connect(
  () => ({}),
  () => ({})
)(Main);

export default MainContainer;

