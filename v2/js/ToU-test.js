
const mock = require('jest-mock');
import React from 'react';
import { Provider } from 'react-intl-redux';
import { mount } from '@pisano/enzyme';
import expect from "expect";
import { put, call, select } from "redux-saga/effects";

import { genSetupComponent } from "tests/ActionWrapper-test";
import MainContainer from "./component";

const pluginState = {
    tous: {
        en: 'Testing ToU',
        sv: 'Testa ToU'
    },
    version: 'test-version'
};

const setupComponent = genSetupComponent(pluginState);

describe("ToU Component", () => {

    it("Renders the splash screen", () => {
        const wrapper = setupComponent({component: <MainContainer />,
                                        overrides: {main: {is_app_loaded: false}}}),
              splash = wrapper.find('div#eduid-splash-screen');

        expect(splash.length).toEqual(1);
    });

    it("Renders", () => {
        const wrapper = setupComponent({component: <MainContainer />}),
              splash = wrapper.find('div#eduid-splash-screen'),
              tou = wrapper.find('div#eduid-tou'),
              buttonAccept = wrapper.find('button#accept-tou-button'),
              buttonReject = wrapper.find('button#reject-tou-button');

        expect(splash.length).toEqual(0);
        expect(tou.length).toEqual(1);
        expect(buttonAccept.length).toEqual(1);
        expect(buttonReject.length).toEqual(1);
        expect(tou.text()).toEqual('Testing ToU');
    });

    it("Renders Svenska", () => {
        const wrapper = setupComponent({component: <MainContainer />,
                                        overrides: {intl: {locale: 'sv'}}}),
              tou = wrapper.find('div#eduid-tou');

        expect(tou.length).toEqual(1);
        expect(tou.text()).toEqual('Testa ToU');
    });
});

