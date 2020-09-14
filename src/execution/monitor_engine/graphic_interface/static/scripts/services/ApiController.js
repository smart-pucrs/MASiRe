class ApiController{
    async fetchData(url){
        const response = await fetch(url);
        
        return await response.json();
    }
}
export default ApiController;