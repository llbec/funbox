import { HardhatRuntimeEnvironment } from 'hardhat/types';

export let HDEnv: HardhatRuntimeEnvironment;

export const setHRE = (_env: HardhatRuntimeEnvironment) => {
    HDEnv = _env;
};

export const sleep = (milliseconds: number) => {
    return new Promise((resolve) => setTimeout(resolve, milliseconds, []));
};