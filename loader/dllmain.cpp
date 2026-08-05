#include <wil/com.h>
#include "WebView2.h"
#include <WebView2EnvironmentOptions.h>
#include <wrl.h>
using namespace Microsoft::WRL;

#define LOADER_API __declspec(dllexport)

LOADER_API HRESULT CreateEnvironmentWithOptions(
	LPCWSTR browserExecutableFolder,
	LPCWSTR userDataFolder,
	LPCWSTR additionalBrowserArguments,
	LPCWSTR language,
	BOOL browserExtensionsEnabled,
	ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler * handler
)
{
	auto options = Microsoft::WRL::Make<CoreWebView2EnvironmentOptions>();

	if (additionalBrowserArguments)
		options->put_AdditionalBrowserArguments(additionalBrowserArguments);

	if (language)
		options->put_Language(language);

	options->put_AreBrowserExtensionsEnabled(browserExtensionsEnabled);

	return CreateCoreWebView2EnvironmentWithOptions(
		browserExecutableFolder,
		userDataFolder,
		options.Get(),
		handler
	);
	return 0;
}

BOOL APIENTRY DllMain(HMODULE, DWORD  ul_reason_for_call, LPVOID)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}
