class ApiController{
    async fetchData(url) {
        const response = await fetch(url);
        
        return await response.json();
    }

    /** 
     * Get match information from API
     * @param apiUrl Url of the api to be fetch
     */
    async getMatchInfo(apiUrl) {
        const url = `${apiUrl}/simulator/info/matches`;

        return await this.fetchData(url);
    }

    /** 
     * Get Map information from API
     * @param apiUrl Url of the api to be fetch
     * @param currentMatch actual match
     */
    async getMapInfo(apiUrl, currentMatch) {
        const url = `${apiUrl}/simulator/match/${currentMatch}/info/map`;

        return await this.fetchData(url);
    }

    /** 
     * Get simulation data from API
     * @param apiUrl Url of the api to be fetch
     * @param currentMatch actual match
     * @param currentStep actual step
     */
    async getSimulationData(apiUrl, currentMatch, currentStep) {
        const url = `${apiUrl}/simulator/match/${currentMatch}/step/${currentStep}`;

        return await this.fetchData(url);
    }

    /** 
     * Get simulation config from API
     */
    async getSimulationConfig(apiUrl) {
        const url = `${apiUrl}/simulator/info/config`;

        return await this.fetchData(url);
    }

    
}
export default ApiController;