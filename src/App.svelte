<script>
  import ChatContainer from './components/ChatContainer.svelte'
</script>

<div class="w-full h-screen bg-gray-900 overflow-hidden flex flex-col">
  <ChatContainer />
</div>

<style global>
  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
</style>
