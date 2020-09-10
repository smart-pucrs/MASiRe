class ApiController{
    async fetchData(url){
        const response = await fetch(url);
        return await response.json();
    }

    async getMatchInfo(apiUrl){
        const url = '${apiUrl}/simulator/info/matches';
        const data = await this.fetchData(url);
        return data
    }

    async getMapInfo(apiUrl, currentMatch){
        const url = '${apiUrl}/simulator/match/${currentMatch}/info/map';
        const data = await this.fetchData(url);
        return data
    }

    async getCurrentStep(apiUrl, currentMatch, currentStep){
        const url = '${apiUrl}/simulator/match/${currentMatch}/step/${currentStep}';
        const data = await this.fetchData(url);
        return data
    }
}
export default ApiController