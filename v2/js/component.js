
import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

import i18n from 'i18n-messages';
import { appFetching, postAction } from "actions/ActionWrapper";
import ActionWrapperContainer from "containers/ActionWrapper";
import EduIDButton from "components/EduIDButton";


class Main extends Component {

    render () {

        return (
            <ActionWrapperContainer>
              <div id="eduid-tou" dangerouslySetInnerHTML={{__html: this.props.tous[this.props.lang]}} />
              <div id="accept-tou-button">
                <EduIDButton onClick={this.props.acceptTOU}>
                  {this.props.l10n('tou.accept')}
                </EduIDButton>
              </div>
            </ActionWrapperContainer>
        );
    }
}

Main.propTypes = {
    tous: PropTypes.object,
    lang: PropTypes.string,
    acceptTOU: PropTypes.func
}

const mapStateToProps = (state, props) => {
    return {
        tous: state.plugin.tous,
        lang: state.intl.locale
    }
};

const mapDispatchToProps = (dispatch, props) => {
    return {
        acceptTOU: function (e) {
            e.preventDefault();
            dispatch(appFetching());
            dispatch(postAction());
        }
    }
};

const MainContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(Main);

export default i18n(MainContainer);

