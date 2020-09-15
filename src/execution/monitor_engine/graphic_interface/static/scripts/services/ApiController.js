class ApiController{
    async fetchData(url) {
        const response = await fetch(url);
        const data = await response.json();
        
        return data;
    }

    async getMatchInfo(apiUrl) {
        const url = `${apiUrl}/simulator/info/matches`;

        return await this.fetchData(url);
    }

    async getMapInfo(apiUrl, currentMatch) {
        const url = `${apiUrl}/simulator/match/${currentMatch}/info/map`;

        return await this.fetchData(url);
    }

    async getSimulationData(apiUrl, currentMatch, currentStep) {
        const url = `${apiUrl}/simulator/match/${currentMatch}/step/${currentStep}`;

        return await this.fetchData(url);
    }

    async getSimulationConfig(apiUrl) {
        const url = `${apiUrl}/simulator/info/config`;

        return await this.fetchData(url);
    }

    
}
export default ApiController;