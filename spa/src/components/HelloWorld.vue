<script>
import axios from "axios";

export default {
  data() {
    return {
      gridColumns: ['key', 'value',],
      data: {},
      searchQuery: '',
    };
  },
  async created() {
    const response = await axios.get(
      "https://dc72xayhuc.execute-api.us-west-2.amazonaws.com/prod/"
    );
    this.data = response.data.Item;
  },
};
</script>

<template>
  <div class="col-md-12">
    <div class="table-responsive">
      <table class="table table-striped table-bordered">
          <thead width="400px">
            <tr>
              <th scope="col" style="padding-right: 200px">Key <i class="fas fa-sort-alpha-down float-right"></i></th>
              <th scope="col">Value<i class="fas fa-sort-alpha-down float-right"></i></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(v, k) in data" :key="v">
              <td>{{k}}</td>
              <td>{{v}}</td>
            </tr>
          </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
th {
  cursor:pointer;
  /* width: 500px !important; */
  white-space: nowrap;
}
tr {
  white-space: nowrap;
}
</style>
